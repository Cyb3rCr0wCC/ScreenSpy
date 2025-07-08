#include <windows.h> // Required for Windows API functions like MessageBox

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Basic Message Box
    // Parameters:
    // 1. hWnd: Handle to the owner window (NULL for no owner).
    // 2. lpText: The message to be displayed.
    // 3. lpCaption: The title of the message box.
    // 4. uType: Specifies the contents and behavior of the message box.
    MessageBox(
        NULL,                               // No owner window
        "This is a simple message.",        // The message text
        "My Simple Message Box",            // The title bar text
        MB_OK                               // Button: OK button
    );

    // Message Box with different icon and buttons
    MessageBox(
        NULL,                               // No owner window
        "This is a question. Do you agree?",// The message text
        "Question Box",                     // The title bar text
        MB_YESNO | MB_ICONQUESTION          // Buttons: Yes, No | Icon: Question mark
    );

    // Message Box with an error icon
    MessageBox(
        NULL,                               // No owner window
        "An error occurred!",               // The message text
        "Error!",                           // The title bar text
        MB_OK | MB_ICONERROR                // Button: OK | Icon: Error (red X)
    );

    // Message Box with information icon and Abort, Retry, Ignore buttons
    int result = MessageBox(
        NULL,                               // No owner window
        "Something went wrong. What do you want to do?", // The message text
        "Action Required",                  // The title bar text
        MB_ABORTRETRYIGNORE | MB_ICONINFORMATION // Buttons: Abort, Retry, Ignore | Icon: Information
    );

    // You can check the return value to see which button was clicked
    switch (result) {
        case IDABORT:
            MessageBox(NULL, "You clicked Abort!", "Result", MB_OK | MB_ICONINFORMATION);
            break;
        case IDRETRY:
            MessageBox(NULL, "You clicked Retry!", "Result", MB_OK | MB_ICONINFORMATION);
            break;
        case IDIGNORE:
            MessageBox(NULL, "You clicked Ignore!", "Result", MB_OK | MB_ICONINFORMATION);
            break;
        default:
            break; // Should not happen for MB_ABORTRETRYIGNORE
    }

    return 0;
}