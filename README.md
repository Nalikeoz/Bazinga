# Bazinga :zap:
Easy & secure remote desktop control and file sharing :octocat:

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installation :minidisc:
The Project uses some libraries that are not included in the basic python 2.7 pack and
in order to use the project you may install the following libraries:
```
pip install pillow
pip install pywin32
pip install pynput
pip install clipboard
pip install pygame
pip install wxPython
pip install numpy
pip install pycrypto
pip install opencv-python
```

## Usage :video_game:
In order to start using Bazinga you'll have to follow the following steps:
1. Open **User.py** with a text editor and change the SERVER_IP const to your main server's local IP address.
2. Run **Main_server.py**.
3. Run **GUI.py** to open Bazinga's UI.

### Register (as Member): 
A Member can choose his own unique remote control username.</br>
In order to register as Member you'll have to enter login username and password (the username you enter will be your remote control username) in the login page, and click the register button, if there isn't already a user with your username you'll get a successfull
registration message, otherwise you'll get an error message.
</br></br>
![Successfull Registration](https://github.com/Nalikeoz/Bazinga/blob/master/images/Successfull_Registration.jpg)

### Login (as Member):
In order to login as Member you'll have to enter your user credentials in the login page and press the login button.
</br></br>
![Login](https://github.com/Nalikeoz/Bazinga/blob/master/images/Login.jpg)

### Login (as Guest):
A Guest gets random remote control credentials (random control username and password).</br>
In order to login as Guest all you'll have to do is to press the "Connect as Guest" Button.
</br></br>
![Login](https://github.com/Nalikeoz/Bazinga/blob/master/images/Guest_Login.jpg)

### Remote Control :computer:
In order to control a remote computer, you may enter the other user's control Username and password
in the relevant inputs in your home page and press the connect button.</br>
If you've entered correct credentials, a chat frame and a remote control window will appear.
</br></br>
![Control](https://github.com/Nalikeoz/Bazinga/blob/master/images/Control.jpg)
</br></br>
![Control Display](https://github.com/Nalikeoz/Bazinga/blob/master/images/control_display.jpg)

### File Transfer :envelope:
In order to transfer files you'll have to follow the following steps:
1. Start a Remote control Session, which will start a chat between both sides (controlled and controlled).
2. Drag a file into the chat (a new download button will appear in the chat).
3. Press the new file's download button in order to download it.
4. The downloaded file will be in a folder called "Downloaded Files".
</br></br>
![File Transfer](https://github.com/Nalikeoz/Bazinga/blob/master/images/file_transfer.jpg)

### Recording Sessions :video_camera:
There are 2 ways to record your remote control sessions.
1. In the home page, under the "Record settings" menu, check the record session tab and your next control sessions will be recorded.
</br></br>
![Record Sessions](https://github.com/Nalikeoz/Bazinga/blob/master/images/record_all_sessions.jpg)
2. In the chat, under the "Record settings" menu, check the record session tab and the current control session will be recorded, or part of it (if you'll uncheck the record tab before the session ends).
</br></br>
![Record Session](https://github.com/Nalikeoz/Bazinga/blob/master/images/record_session.jpg)
* **The recordings are .avi files and saved at a folder called "Recordings".**

## Encryption :closed_lock_with_key:
All of Bazinga's traffic is encrypted with AES based encryption.
You may change the AES encryption key, by changing the value of the ENC_KEY in the AESCipher.py file.
</br>
```python
ENC_KEY = md5('the AES key').hexdigest()
```

## Built With :hammer:
* [PyCharm](https://www.jetbrains.com/pycharm/) - Working framework.
* [Python 2.7](https://www.python.org/)         - Programming language.

## Author :pencil:
* **Nadav Shamir** - [Nalikeoz](https://github.com/Nalikeoz)
