### Intro

We need three machine in order to run this attack:

- **Server** ->  This is our server machine that setup all the work and listens incoming connection from victim
- **Builder** -> This is our builder machine to compile our *client.py* to executable file. We need exact same operation system as victim use **windows** machine to compile that script to windows machine or use **linux** to compile that script for linux(x11) machines
- **Victim** ->  This is our Victim machine which we will infect and capture screen real time. 

ScreenSpy is a repository that contains followings:
   -   helper/helper.c - code to encrypt and decrypt. e.g: *helper.bin encode/decode <string>*
   -   scripts/change.sh - bash script to change parameters like hostnames, port numbers ... from source codes before compiling.
   -   scripts/prepare.sh - prepares the server.
   -   src/client.py - malware that connect to server to share its screen real time
   -   src/server.py - server waiting for incoming connection.
   -   src/runner.exe - to run client.exe as background process 
   -   src//stager/screenshareStage.ino - arduino code to prepare stager BadUsb
   -   src/stager/stager.ps1 - stager powershell script that badusb runs from url
   -   nginx.conf - nginx web server config

NOTE!: This program tested on Windows10, Linux(X11) and there no guarantee that will work for other OSs.

#### Compile python script to executable
In order to compile *client.py* script for linux(X11) or Windows:
```bash
git clone https://github.com/Cyb3rCr0wCC/ScreenSpy
cd ScreenSpy
pip3 install pyinstaller
pyinstaller ./client.py --onefile
```

After running above commands you will get folder named *dist*, this contian our executable.

Copy your compiled executable to your **Server** builds folder in your cloned repo.

``````bash
git clone https://github.com/Cyb3rCr0wCC/ScreenSpy
cd ScreenSpy
mkdir builds
### Copy compiled client.py to there
``````

#### Prepare the Server

There are two options you can prepare your **Server** for this attack

Automated:

``````bash
cd scripts
bash change.sh -h <server_Ip> -p <port>
bash prepare.sh	
``````

Manual (root):

you can check prepare.sh commands



#### Prepare BadUsb

Last step is preparing our BadUsb that will do all the job when plugged into victim's computer. 

I used Arduino as a Ide to compile and upload *src/stager/scrennshareStager.ino* code into our BadUsb.

I used Atmega32U4  as my BadUsb.

You can download arduino release from this: [arduino](https://www.arduino.cc/en/software)

Open up arduino and paste code inside *"scrennshareStager.ino"*



#### Compile client.py 

You need to use same os as your target's machine and run following commnad:

``````powershell
pyinstaller client.py --onefile
``````

Then after getting compiled binary (**windows**: client.exe; **linux** - client) copy that file into your server's webroot (**default**-/var/www/html)



#### Your are ready:

Both your server and your badusb are ready to operate.

Run your server program(***on you server machine***):

``````
python3 server.py
``````

Then plug your badusb into your target machine

after few seconds your stager powershell script will run.



### Conclusion

Developing tools that interact with security products like AV, EDR, and firewalls is an ongoing challenge. While I strive to **obfuscate** and adapt these codes to bypass the latest versions of such software, there's no absolute guarantee of universal bypass due to continuous advancements in security products.

------

I am committed to enhancing these programs, and this repository is **open for contributions** from anyone who wishes to help make them more robust and effective. Your insights and efforts are highly valued!

