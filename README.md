# Bazinga
Easy & secure remote desktop control and file sharing :octocat:

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installation
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

## Usage
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

### Remote Control
In order to control a remote computer, you may enter the other user's control Username and password
in the relevant inputs in your home page and press the connect button.</br>
If you've entered correct credentials, a remote control window will appear.
</br></br>
![Control](https://github.com/Nalikeoz/Bazinga/blob/master/images/Control.jpg)
</br></br>
![Control Display](https://github.com/Nalikeoz/Bazinga/blob/master/images/control_display.jpg)
