import socket
from PIL import Image, ImageGrab
from win32api import GetSystemMetrics
from threading import Thread
from Handler import *
from Messages import *
import wx
import StringIO
from pynput import keyboard
from pynput import mouse
import time
import clipboard
from VideoWriter import VideoWriter

FILES_SOCKET_PORT = 8081
PORT = 8082
IMAGE_SUFFIX = 'IMG'  # used to define if a string is an image.
KEYBOARD = keyboard.Controller()
MOUSE = mouse.Controller()
Y_PIXELS_TO_SCROLL_UP = 100
Y_PIXELS_TO_SCROLL_DOWN = -100


class Controlled(object):
    def __init__(self, is_recording):
        """
        The constructor function of the Controlled object.
        """
        self.client_socket = socket.socket()
        self.files_socket = socket.socket()  # used to download and send files.
        self.events_handler = EventsHandler()  # used to handle events.
        self.is_recording = is_recording
        self.video_writer = None
        if self.is_recording:
            self.video_writer = VideoWriter()

    def connect_to_controller(self, controller_ip):
        """

        :param controller_ip: the ip address the controller.
        the function connects to the remote controller server.
        """
        time.sleep(0.1)
        self.client_socket.connect((controller_ip, PORT))
        self.files_socket.connect((controller_ip, FILES_SOCKET_PORT))
        self.controller_ip = controller_ip
        print 'connected to controller'

    @staticmethod
    def get_screen_resolution():
        """

        :return: the function returns the user screen resolution.
        * needed to make a ratio between the controller window size
        and the user screen resolution so the mouse pos will be accurate.
        """
        screen_width = GetSystemMetrics(0)
        screen_height = GetSystemMetrics(1)
        screen_resolution = ScreenResolutionMessage(screen_width, screen_height)
        return screen_resolution

    # TODO delete this function and change all of its calls!
    def send_message(self, message, to_pickle):
        self.events_handler.send_message(message, to_pickle, self.client_socket)

    def get_screenshot_data(self):
        """

        :return: this function takes a screen shot, resize it with ratio,
        compress it and returns it as raw data.
        """
        image = ImageGrab.grab().resize(self.events_handler.image_size, Image.ANTIALIAS)
        output = StringIO.StringIO()
        image.save(output, format="JPEG", quality=95)
        data = output.getvalue()
        return data

    def send_screenshot(self):
        """
        the function sends screen shots to the controller.
        """
        while self.events_handler.running:
            try:
                image_data = self.get_screenshot_data() + IMAGE_SUFFIX
                self.events_handler.send_message(image_data, False, self.client_socket)
                if self.is_recording:
                    image_data_without_suffix = image_data[:-len(IMAGE_SUFFIX)]
                    Thread(target=self.video_writer.write, args=[image_data_without_suffix]).start()
            except socket.error:
                self.close_connection()
            except AttributeError:
                pass

    def define_message_type(self, message):
        """

        :param message: the controller's message.
        :return: the function define the message type and calls
        the wanted function.
        """
        if isinstance(message, MousePress):
            MOUSE.press(MOUSE_INDICATORS[message.mouse_click_indicator])

        elif isinstance(message, ChatMessage):
            #wx.CallAfter(wx.GetApp().chat_frame.add_message, self.controller_ip + '> ' + message.message)
            wx.CallAfter(wx.GetApp().chat_frame.add_message, self.controller_ip, message.message)

        elif isinstance(message, FileMessage):
            wx.CallAfter(wx.GetApp().chat_frame.main_panel.chat_log.new_file_message, message.file_path)

        elif isinstance(message, RequestFile):
            Thread(target=self.events_handler.send_file, args=[message.file_path, self.files_socket]).start()

        elif isinstance(message, FileNotExists):
            self.events_handler.messages_handler.running = False  # in order to get the recv thread out of the while.

        elif isinstance(message, MouseRelease):
            MOUSE.release(MOUSE_INDICATORS[message.mouse_click_indicator])

        elif isinstance(message, MouseScroll):
            if message.mouse_click_indicator == SCROLL_UP_INDICATOR:
                MOUSE.scroll(0, Y_PIXELS_TO_SCROLL_UP)
            elif message.mouse_click_indicator == SCROLL_DOWN_INDICATOR:
                MOUSE.scroll(0, Y_PIXELS_TO_SCROLL_DOWN)

        elif isinstance(message, MouseMotion):
            MOUSE.position = (message.x, message.y)

        elif isinstance(message, KeyPress):
            KEYBOARD.press(message.key)

        elif isinstance(message, KeyRelease):
            KEYBOARD.release(message.key)

        elif isinstance(message, ImageSizeChange):
            self.events_handler.image_size = message.image_size

        elif isinstance(message, CopyValue):
            clipboard.copy(message.copied_data)

        elif isinstance(message, Disconnect):
            self.close_connection()

    def run(self):
        """
        this function "runs" the controlled object, it calls the wanted
        functions so the conversation will be as wanted.
        """
        self.send_message(self.get_screen_resolution(), True)  # send screen resolution
        self.screenshots_thread = Thread(target=self.send_screenshot).start()  # screenshots sender
        while self.events_handler.running:
            try:
                message = self.events_handler.receive_message(self.client_socket)
                self.define_message_type(message)
            except socket.error:
                self.close_connection()

    def close_connection(self):
        """
        the function stops the connection between the controller and the controlled side.
        """
        self.events_handler.running = False
        self.client_socket.close()
        self.files_socket.close()
        try:
            self.video_writer.close()
        except Exception as e:
            pass

