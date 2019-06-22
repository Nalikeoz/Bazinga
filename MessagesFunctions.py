import pickle
import time
from Messages import *
import wx
from AESCipher import AESCipher
import os

LEN_OF_LENGTH = 6
PICKLE_BIT = 'T'
IMAGE_SUFFIX = 'IMG'
START_OF_ENC = 'START'
BYTES_AMOUNT = 1024
READ_BIN_MODE = 'rb'
WRITE_BIN_MODE = 'wb'
DEFAULT_FILE_NAME = 'file'
FILES_FOLDER = 'Downloaded Files\\'
try:
    os.mkdir('Downloaded Files')
except WindowsError:
    pass

class MessagesFunctions(object):

    def __init__(self):
        self.file_number = 0
        self.encryption_suite = AESCipher()

    def get_enc_message(self, message_length, client_socket):
        """
        :param client_socket: the client socket.
        :param message_length: the length of the message the was received.
        :return: the message.
        """
        try:
            message = self.get_message_content(message_length, client_socket)
            if message.find(IMAGE_SUFFIX) != -1:
                return self.encryption_suite.decrypt_image(message[:-len(IMAGE_SUFFIX)])
            decrypted_message = self.encryption_suite.decrypt(message)
            if decrypted_message[-1:] == PICKLE_BIT:
                return pickle.loads(decrypted_message)

            return message
        except Exception:
            pass

    @staticmethod
    def get_message_content(message_length, client_socket):
        content = ""
        while (len(content) != message_length):
            content += client_socket.recv(message_length - len(content))
        return content

    @staticmethod
    def get_message_length(client_socket):
        """
        the function receives the length of the message.
        :return: the message length
        """
        message_length = ""
        while (len(message_length) != LEN_OF_LENGTH):
            message_length += client_socket.recv(LEN_OF_LENGTH - len(message_length))
        try:
            return int(message_length)
        except ValueError:
            pass

    def receive_message(self, client_socket):
        """

        :param client_socket: the client to receive the message from.
        :return: the client's message.
        """
        message_length = self.get_message_length(client_socket)
        message = self.get_enc_message(message_length, client_socket)
        return message

    def get_file(self, file_suffix, client_socket):
        """
        :param file_suffix: the suffix of the original file (exm: .txt, .docx).
        :param client_socket: the socket to receive data from.
        """
        # TODO check whether a file + number is already exists.
        self.file_number += 1
        file_length = self.get_message_length(client_socket)
        file_data = self.get_message_content(file_length, client_socket)
        pickled_file = ''
        try:
            pickled_file = pickle.loads(file_data)
        except (KeyError, IndexError, ValueError, ImportError):
            pass

        if isinstance(pickled_file, FileNotExists):
            wx.CallAfter(wx.GetApp().chat_frame.main_panel.chat_log.new_text_message, FileNotExists())
        else:
            f = open(FILES_FOLDER + DEFAULT_FILE_NAME + str(self.file_number) + file_suffix, WRITE_BIN_MODE)
            f.write(file_data)
            f.close()

    def send_file(self, file_path, client_socket):
        """
        @param file_path: the file's path in the sender's pc.
        @param client_socket: the socket of the sender.
        the function sends a file over the files socket.
        """
        try:
            print '- - - - Sending File - - - -'
            f = open(file_path, READ_BIN_MODE)
            print '[1] opened file'
            file_content = f.read()
            print '[2] read file data'
            client_socket.send(str(len(file_content)).zfill(LEN_OF_LENGTH))
            print '[3] send file data length'
            time.sleep(0.1)
            client_socket.send(file_content)
            print '[4] send file data'
            f.close()
            print '[5] closed file'
        except IOError:
            self.send_message(FileNotExists(), True, client_socket)
            print '[-1] file not exists'

    def send_enc_message(self, message, to_pickle, client_socket):
        """
        :param message: the message that will be sent(as its encrypted form).
        :param to_pickle: a boolean the means rather to pickle the message or not to.
        :param client_socket: the socket to sent the message from.
        """
        if to_pickle:
            message = pickle.dumps(message) + PICKLE_BIT
        if message.find(IMAGE_SUFFIX) != -1:
            encrypted_message = self.encryption_suite.encrypt_image(message[:-len(IMAGE_SUFFIX)])
        else:
            encrypted_message = self.encryption_suite.encrypt(message)

        client_socket.send(str(len(encrypted_message)).zfill(LEN_OF_LENGTH))
        client_socket.send(encrypted_message)

    @staticmethod
    def send_message(message, to_pickle, client_socket):
        if to_pickle:
            message = pickle.dumps(message) + PICKLE_BIT

        client_socket.send(str(len(message)).zfill(LEN_OF_LENGTH))
        client_socket.send(message)
