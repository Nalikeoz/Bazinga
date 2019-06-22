import socket
import pygame
from Handler import *  # EventsHandler, IMAGE_SIZE
from Messages import *
import StringIO
import wx
from threading import Thread
from VideoWriter import VideoWriter

IP = '0.0.0.0'
PORT = 8082
FILES_SOCKET_PORT = 8081
SCREEN_NAME = 'SquadViewer'
IMAGE_SUFFIX = 'IMG'


class Controller(object):
    def __init__(self, controlled_ip, is_recording):
        """
        the constructor function of the Controller object
        @param controlled_ip: the ip address of the controlled user.
        @param is_recording: a boolean meas whether to record the screen or not.
        """
        self.is_recording = is_recording  # a boolean means whether to record the screen or not.
        self.server_socket = socket.socket()
        self.server_files_socket = socket.socket()  # used to download and send files.
        self.events_handler = EventsHandler()  # used to handle events.
        self.video_writer = None
        if self.is_recording:
            self.video_writer = VideoWriter()  # used to record the control session.
        self.controlled_ip = controlled_ip

    def bind_socket(self):
        """
        the function binds the socket of the controller.
        """
        self.server_socket.bind((IP, PORT))
        self.server_files_socket.bind((IP, FILES_SOCKET_PORT))
        self.server_files_socket.listen(1)
        self.server_socket.listen(1)
        print 'Started server on: ' + IP + ':' + str(PORT)
        self.accept_user()

    def accept_user(self):
        """
        the function accepts the controlled user.
        """
        print 'Waiting for connection.. '
        self.client_socket, self.client_address = self.server_socket.accept()
        #self.client_file_socket, client_address = self.files_socket.accept()
        self.files_socket, client_address = self.server_files_socket.accept()
        print 'Got connection from ' + self.client_address[0]

    def get_display(self):
        """

        :return: a pygame screen(where the screen will be shown)
        """
        pygame.init()
        screen = pygame.display.set_mode(self.events_handler.image_size, pygame.RESIZABLE)
        pygame.display.set_caption(SCREEN_NAME, SCREEN_NAME)
        return screen

    def update_display(self, screen, image_data):
        """

        :param screen: the pygame screen where the controlled screen is shown.
        the function updates the image on the screen.
        """
        image = self.get_image(image_data)
        self.change_image_on_screen(screen, image)

    @staticmethod
    def get_image(image_data):
        """
        :return: the new screen shot from the controlled machine.
        """
        #image_data = self.events_handler.receive_message(self.client_socket)
        output = StringIO.StringIO(image_data)
        image = pygame.image.load(output)
        return image

    @staticmethod
    def change_image_on_screen(screen, image):
        """
        :param screen: the pygame screen where the controlled screen is shown.
        :param image: the new screen shot from the controlled.
        the function changes the image on the screen.
        """
        screen.blit(image, (0, 0))
        #screen.blit(pygame.transform.scale(image, self.events_handler.image_size), (0, 0))
        pygame.display.flip()

    def define_message_type(self, message):
        """

        :param message: the controlled user message.
        the function define the message type and calls the wanted
        function.
        """
        if isinstance(message, ScreenResolutionMessage):
            self.controlled_screen_res = [message.width, message.height]

        elif isinstance(message, FileMessage):
            wx.CallAfter(wx.GetApp().chat_frame.main_panel.chat_log.new_file_message, message.file_path)

        elif isinstance(message, RequestFile):
            Thread(target=self.events_handler.send_file, args=[message.file_path, self.files_socket]).start()

        elif isinstance(message, FileNotExists):
            self.events_handler.messages_handler.running = False  # in order to get the recv thread out of the while.

        elif isinstance(message, ChatMessage):
            #wx.CallAfter(wx.GetApp().chat_frame.add_message, self.controlled_ip + '> ' + message.message)
            wx.CallAfter(wx.GetApp().chat_frame.add_message, self.controlled_ip, message.message)

        else:
            try:
                self.update_display(self.screen, message)
                if self.is_recording:
                    Thread(target=self.video_writer.write, args=[message]).start()
            except Exception:
                pass
            
    def run(self):
        """
        this function "runs" the controller object, it calls the wanted
        functions so the conversation will be as wanted.
        """
        self.screen = self.get_display()
        self.events_handler.handle_keyboard_events(self.client_socket)
        while self.events_handler.running:
            try:
                message = self.events_handler.receive_message(self.client_socket)
                self.define_message_type(message)
                self.events_handler.handle_mouse_events(self.screen, self.client_socket, self.controlled_screen_res)
            except Exception as e:
                self.events_handler.running = False
                raise e
        self.close()

    def close(self):
        """
        the function is called at the end of the control session, in order to finish the session.
        the function closes all the working tasks.
        """
        self.client_socket.close()
        self.server_socket.close()
        self.server_files_socket.close()
        try:
            self.video_writer.close()
        except Exception as e:
            pass
        print '[CONTROLLER] Control session was ended.'

