import pyotp
import time
import json
import subprocess
from cryptography.fernet import Fernet
import qrcode

# Function to generate a random secret key
def generate_secret_key():
    return pyotp.random_base32()

# Function to generate a TOTP URI
def generate_totp_uri(secret_key, issuer, label):
    totp = pyotp.TOTP(secret_key)
    return totp.provisioning_uri(label, issuer_name=issuer)

# Function to generate a QR code for the TOTP URI and display it in the terminal
def generate_and_display_qr_code(uri):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    qr.print_ascii()

# Function to generate a TOTP code
def generate_totp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

# Function to change the Windows password
def change_windows_password(username, new_password):
    command = ['net', 'user', username, new_password]
    try:
        subprocess.run(command, check=True)
        #print(f"Password changed successfully! Current password: {new_password}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# Function to decrypt data
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

if __name__ == "__main__":
    # Load or generate secret key
    try:
        with open("secret_key.json", "r") as f:
            data = json.load(f)
            encrypted_key = data['encrypted_key']
            # Load the encryption key
            with open("encryption_key.txt", "rb") as key_file:
                encryption_key = key_file.read()
            # Decrypt the secret key
            decrypted_key = decrypt_data(encrypted_key, encryption_key)
            secret_key = decrypted_key
    except (FileNotFoundError, ValueError):
        # If the secret key file doesn't exist or decryption fails, generate a new key
        secret_key = generate_secret_key()
        # Generate and display the QR code for the first-time setup
        issuer = 'TOTP Hypex'
        label = 'Admin_PC'
        uri = generate_totp_uri(secret_key, issuer, label)
        generate_and_display_qr_code(uri)
        # Generate an encryption key
        encryption_key = Fernet.generate_key()
        # Encrypt the secret key
        encrypted_key = encrypt_data(secret_key, encryption_key)
        # Save the encrypted secret key to a file
        with open("secret_key.json", "w") as f:
            json.dump({'encrypted_key': encrypted_key.decode()}, f)
        # Save the encryption key to a file
        with open("encryption_key.txt", "wb") as key_file:
            key_file.write(encryption_key)

    username = 'admin'

    while True:
        totp_code = generate_totp(secret_key)
        change_windows_password(username, totp_code)
        time.sleep(2)
