# -*- coding: utf-8 -*-
import socket
from Messages import *
from MessagesFunctions import MessagesFunctions
import wx
from Controlled import *
from Controller import *
import time

SERVER_IP = 'localhost' #change it to the main server's IP address.
SERVER_PORT = 8080
LEN_OF_LENGTH = 6
WRONG_CREDS_ERROR = 'Wrong ID or Password'
USERNAME_ALREADY_EXISTS_ERROR = 'Username already exists!'
USERNAME_DOES_NOT_EXISTS_ERROR = 'There\'s no user called '
REGISTERED_SUCCESSFULLY = 'Registered Successfully'
ALREADY_SENT_REQUEST = 'You have already sent this user friend request.'


class User(object):
    def __init__(self):
        self.id = ''
        self.password = ''
        self.mess_handler = MessagesFunctions()
        self.is_recording = False
        self.running = True
        self.user_type = None

    def connect_to_the_server(self):
        self.client_socket = socket.socket()
        self.client_socket.connect((SERVER_IP, SERVER_PORT))
        print 'connected to main server'

    def control(self, controlled_ip):
        self.user_type = Controller(controlled_ip, self.is_recording)
        self.user_type.bind_socket()
        self.user_type.run()

    def get_controlled(self, controller_ip):
        self.user_type = Controlled(self.is_recording)
        self.user_type.connect_to_controller(controller_ip)
        self.user_type.run()

    def disconnect_from_server(self):
        disconnect_message = Disconnect()
        self.mess_handler.send_enc_message(disconnect_message, True, self.client_socket)
        self.client_socket.close()

    def start_conversation(self, conv_message):
        wx.CallAfter(wx.GetApp().frame.Hide)
        wx.CallAfter(wx.GetApp().create_chat_frame)

        if isinstance(conv_message.role, RoleController):
            self.control(conv_message.user_info.ip)
        elif isinstance(conv_message.role, RoleControlled):
            self.get_controlled(conv_message.user_info.ip)

        wx.CallAfter(wx.GetApp().chat_frame.Hide)
        wx.CallAfter(wx.GetApp().frame.Show)
        self.mess_handler.send_enc_message(DoneSession(), True, self.client_socket)

    def define_message_type(self, message):
        if isinstance(message, StartConversation):
            self.start_conversation(message)

        elif isinstance(message, GetID):
            self.id = message.user_id
            time.sleep(0.1)
            wx.CallAfter(wx.GetApp().frame.set_id, self.id)

        elif isinstance(message, GetPassword):
            self.password = message.user_password
            time.sleep(0.1)
            wx.CallAfter(wx.GetApp().frame.set_password, self.password)

        elif isinstance(message, UserAlreadyExists):
            wx.CallAfter(wx.GetApp().login_frame.set_error, USERNAME_ALREADY_EXISTS_ERROR)

        elif isinstance(message, SuccessfulLogin):
            self.user_type = message.user_type
            wx.CallAfter(wx.GetApp().create_main_frame)
            wx.CallAfter(wx.GetApp().login_frame.Close)

        elif isinstance(message, SuccessfulRegister):
            wx.CallAfter(wx.GetApp().login_frame.set_error, REGISTERED_SUCCESSFULLY)

        elif isinstance(message, WrongCredentials):
            wx.CallAfter(wx.GetApp().frame.set_error, WRONG_CREDS_ERROR)

        elif isinstance(message, WrongLoginCreds):
            wx.CallAfter(wx.GetApp().login_frame.set_error, WRONG_CREDS_ERROR)

    def receive_message(self):
        while self.running:
            try:
                message = self.mess_handler.receive_message(self.client_socket)
                self.define_message_type(message)

            except RuntimeError as e:
                print e
            except socket.error:
                self.client_socket.close()
                self.running = False

