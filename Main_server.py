# -*- coding: utf-8 -*-
import socket
from select import select
import random
import string
from Messages import *
from MessagesFunctions import MessagesFunctions
import time
from threading import Thread
from DataBase import DataBase

IP = '0.0.0.0'
MEMBER_USER_TYPE = 'member'
GUEST_USER_TYPE = 'guest'
PORT = 8080
LEN_OF_LENGTH = 6
PASSWORD_LENGTH = 6
MIN_VALUE_OF_ID = 100000000
MAX_VALUE_OF_ID = 999999999
TIME_TO_RESET_PASSWORD = 120  # 120 seconds


class MainServer(object):
    def __init__(self):
        """
        the constructor function of the MainServer object.
        """
        self.server_socket = socket.socket()
        self.database = DataBase()
        self.online_users = {}  # {socket:UserInfo object}
        self.pending_users = {}  # {socket:ip address}
        self.mess_handler = MessagesFunctions()
        self.running = True

    def start_server(self):
        """
        the function binds the socket and starts listening for new connections.
        """
        self.server_socket.bind((IP, PORT))
        print '================================================'
        print '[+] Starting server on: ' + IP + ':' + str(PORT)
        print '================================================'
        self.server_socket.listen(1)
        Thread(target=self.new_password_timer).start()

    def accept_user(self):
        """
        the function accepts a new user and adds him to the pending users dictionary.
        """
        client_socket, client_address = self.server_socket.accept()
        client_ip_address = client_address[0]
        self.pending_users[client_socket] = client_ip_address
        print '[+] New Pending User [' + str(client_ip_address) + ']'

    def guest_login(self, user_socket):
        user_id = self.generate_id()
        password = self.generate_password()
        self.new_online_user(GUEST_USER_TYPE, user_id, password, user_socket)
        print '[+] New Online User (Guest).'

    def member_login(self, connection_message, user_socket):
        username = connection_message.username
        connection_password = connection_message.password
        if self.database.does_user_exists(username, connection_password):
            self.new_online_user(MEMBER_USER_TYPE, username, self.generate_password(), user_socket)
            print '[+] New Online User (Member).'
        else:
            self.mess_handler.send_enc_message(WrongLoginCreds(), True, user_socket)

    def new_online_user(self, user_type, username, password, user_socket):
        """
        adds user to the online users dict.
        """
        user_ip_address = self.pending_users[user_socket]
        user = UserInfo(user_type, username, password, user_ip_address)
        del self.pending_users[user_socket]
        self.online_users[user_socket] = user
        self.mess_handler.send_enc_message(SuccessfulLogin(user_type), True, user_socket)
        self.send_id_pass(user_socket, username, password)

    def register(self, username, password, user_socket):
        if not self.database.does_username_exists(username):
            self.database.add_user(username, password)
            self.mess_handler.send_enc_message(SuccessfulRegister(), True, user_socket)

        else:
            self.mess_handler.send_enc_message(UserAlreadyExists(), True, user_socket)

    def send_id_pass(self, client_socket, new_id, new_password):
        """
        :param client_socket: the socket of the receiver.
        :param new_id: the new id to send to the client.
        :param new_password: the new password to send to the client.
        """
        user_id = GetID(new_id)
        user_password = GetPassword(new_password)
        self.mess_handler.send_enc_message(user_id, True, client_socket)  # send id
        self.mess_handler.send_enc_message(user_password, True, client_socket)  # send password

    def new_password_timer(self):
        """
        the function sends new password to all users every 2 minutes.
        """
        while self.running:
            try:
                time.sleep(TIME_TO_RESET_PASSWORD)
                for client_socket in self.online_users:
                    new_password = GetPassword(self.generate_password())
                    self.mess_handler.send_enc_message(new_password, True, client_socket)
                    self.online_users[client_socket].change_password(new_password.user_password)
            except socket.error:
                self.remove_user(client_socket)

    def remove_user(self, client_socket):
        """
        :param client_socket: the socket of the client that will be removed.
        the function remove a users from the users dictionary.
        """
        if client_socket in self.online_users:
            del self.online_users[client_socket]
            client_socket.close()
            print '[+] User has Been Disconnected.'

    def generate_password(self):
        """
        return: random password(string)
        """
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(PASSWORD_LENGTH)])
        while self.password_exist(password):
            password = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(PASSWORD_LENGTH)])
        return password

    def generate_id(self):
        """
        return: random id(int).
        """
        user_id = random.randint(MIN_VALUE_OF_ID, MAX_VALUE_OF_ID)
        while self.id_exist(user_id):
            user_id = random.randint(MIN_VALUE_OF_ID, MAX_VALUE_OF_ID)
        return user_id

    def password_exist(self, password):
        """
        :param password: the password to check if exists.
        return: True/False that references whether there is someone with that password or not.
        """
        for user in self.online_users.values():
            if user.password == password:
                return True
        return False

    def id_exist(self, user_id):
        """
        :param user_id: the id to check if exists.
        return: True/False that references whether there is someone with that id or not.
        """
        for user in self.online_users.values():
            if user.user_id == user_id:
                return True
        return False

    def get_user(self, user_id, user_pass):
        """
        :param user_id: id of the wanted user(int).
        :param user_pass: password of the wanted user(string).
        return: True/False whether there's a user with the following info.
        """
        for user in self.online_users.values():
            if str(user_id) == str(user.user_id) and str(user_pass) == str(user.password):
                return user
        return None  # no such user

    def wrong_credentials(self, client_socket):
        self.mess_handler.send_enc_message(WrongCredentials(), True, client_socket)

    def get_socket_by_userinfo(self, user):
        """
        :param user: UserInfo object.
        return: socket of the user with the UserInfo info, if the user doesnt exists return None.
        """
        for socket, user_info in self.online_users.items():
            if user_info is user:
                return socket
        return None

    def control_user(self, control_user_message, client_socket):
        controlled_user_id = control_user_message.remote_user_id  # the id of the user you want to control.
        controlled_user_pass = control_user_message.remote_user_password  # the pass of the user you want to control.
        controlled_user = self.get_user(controlled_user_id, controlled_user_pass)  # the UserInfo object of the user you want to control.
        # if user equals to None it means that there is no such user.
        if isinstance(controlled_user, UserInfo) and controlled_user.can_start_session:
            controlled_user_socket = self.get_socket_by_userinfo(controlled_user)
            self.mess_handler.send_enc_message(StartConversation(RoleControlled(), self.online_users[client_socket])
                                           , True, controlled_user_socket)
            self.mess_handler.send_enc_message(StartConversation(RoleController(), controlled_user),
                                           True, client_socket)
            self.disable_user(client_socket)
            self.disable_user(controlled_user_socket)
        else:
            self.wrong_credentials(client_socket)

    def disable_user(self, user_socket):
        self.online_users[user_socket].can_start_session = False
        print '[+] User Disabled.'

    def enable_user(self, user_socket):
        self.online_users[user_socket].can_start_session = True
        print '[+] Enabled User.'

    def define_message_type(self, message, client_socket):
        if isinstance(message, ControlUser):
            self.control_user(message, client_socket)

        elif isinstance(message, GuestConnection):
            self.guest_login(client_socket)

        elif isinstance(message, MemberConnection):
            self.member_login(message, client_socket)

        elif isinstance(message, RegisterMessage):
            self.register(message.username, message.password, client_socket)

        elif isinstance(message, DoneSession):
            self.enable_user(client_socket)

        elif isinstance(message, Disconnect):
            self.remove_user(client_socket)

    def handle_server(self):
        while self.running:
            users = self.online_users.keys() + self.pending_users.keys()
            rlist, wlist, xlist = select(users + [self.server_socket], [], [])

            for client_socket in rlist:
                if client_socket is self.server_socket:
                    self.accept_user()

                else:
                    try:
                        message = self.mess_handler.receive_message(client_socket)
                        self.define_message_type(message, client_socket)

                    except socket.error:
                        self.remove_user(client_socket)


def main():
    server = MainServer()
    server.start_server()
    server.handle_server()


if __name__ == '__main__':
    main()
