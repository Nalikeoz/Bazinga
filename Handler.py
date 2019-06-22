# -*- coding: utf-8 -*-
import socket
from pynput import keyboard
import pickle
from Messages import *
from pynput.mouse import Button
import pygame
from pygame.locals import *
import clipboard
import time
from MessagesFunctions import MessagesFunctions


PICKLE_BIT = 'T'
MOUSE_IN_THE_SCREEN_FLAG = 1
LEN_OF_LENGTH = 8
LEFT_CLICK_INDICATOR = 1
MIDDLE_CLICK_INDICATOR = 2
RIGHT_CLICK_INDICATOR = 3
SCROLL_UP_INDICATOR = 4
SCROLL_DOWN_INDICATOR = 5
MOUSE_MOTION = 6
MIN_SCREEN_WIDTH = 805
MIN_SCREEN_HEIGHT = 605
MOUSE_INDICATORS = {LEFT_CLICK_INDICATOR: Button.left,
                    MIDDLE_CLICK_INDICATOR: Button.middle,
                    RIGHT_CLICK_INDICATOR: Button.right}

COPY_KEYBOARD_COMBINATIONS = [
    {keyboard.Key.ctrl_l, keyboard.KeyCode(char='c')},
    {keyboard.Key.ctrl_l, keyboard.KeyCode(char='C')},
    {keyboard.Key.ctrl_r, keyboard.KeyCode(char='c')},
    {keyboard.Key.ctrl_r, keyboard.KeyCode(char='C')}
]


class EventsHandler(object):
    def __init__(self):
        self.running = True
        self.image_size = (MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT)
        self.messages_handler = MessagesFunctions()
        self.current_key_combinations = set()

    def send_file(self, file_path, client_socket):
        self.messages_handler.send_file(file_path, client_socket)

    def receive_file(self, file_name, client_socket):
        self.messages_handler.get_file(file_name, client_socket)

    def receive_message(self, client_socket):
        """

        :param client_socket: the socket of the client.
        :return: the message that was received.
        """
        try:
            message = self.messages_handler.receive_message(client_socket)
            return message
        except socket.error:
            client_socket.close()

    def send_message(self, message, to_pickle, client_socket):
        """
        :param message: the message that will be sent.
        :param to_pickle: a boolean the means rather to pickle the message or not to.
        :param client_socket: the socket to sent the message to.
        """
        self.messages_handler.send_enc_message(message, to_pickle, client_socket)

    def get_screen_ratio_coordinates(self, user_screen_resolution, mouse_x, mouse_y):
        """
        :param user_screen_resolution: the controlled user screen resolution.
        :param mouse_x: the x value of the mouse pos.
        :param mouse_y: the y value of the mouse pos.
        returns a list of the new x and y values with a ratio to the controlled user screen resolution.
        """
        width_ratio = float(user_screen_resolution[0]) / float(self.image_size[0])
        height_ratio = float(user_screen_resolution[1]) / float(self.image_size[1])
        mouse_x = mouse_x * width_ratio
        mouse_y = mouse_y * height_ratio
        return [mouse_x, mouse_y]

    def handle_mouse_events(self, screen, client_socket, controlled_screen_resolution):
        """
        :param screen: the pygame screen of the controller.
        :param client_socket: the controller's socket.
        :param controlled_screen_resolution: the controlled user screen resolution.
        the function handles mouse events.
        """
        # TODO: make this function better.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.keyboard_listener.stop()
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == SCROLL_UP_INDICATOR or event.button == SCROLL_DOWN_INDICATOR:
                    mouse_press_command = MouseScroll(event.button)
                else:
                    mouse_press_command = MousePress(event.button)
                self.send_message(mouse_press_command, True, client_socket)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == SCROLL_UP_INDICATOR or event.button == SCROLL_DOWN_INDICATOR:
                    mouse_release_command = MouseScroll(event.button)
                else:
                    mouse_release_command = MouseRelease(event.button)
                self.send_message(mouse_release_command, True, client_socket)

            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_x, mouse_y = self.get_screen_ratio_coordinates(controlled_screen_resolution, mouse_x, mouse_y)
                mouse_motion_command = MouseMotion(mouse_x, mouse_y)
                self.send_message(mouse_motion_command, True, client_socket)

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                self.check_min_screen_size(width, height)
                screen = pygame.display.set_mode(self.image_size, pygame.RESIZABLE)
                self.send_message(ImageSizeChange(self.image_size), True, client_socket)

    def check_min_screen_size(self, width, height):
        """
        @param width: the new width of the screen.
        @param height: the new height of the screen.
        the function is called when a screen resize event happens, it gets
        the new screen's widht\height and check if he fits the minimum screen size.
        if it is, the function leaves it as is, otherwise it changes the screen size to the min size.
        """
        if width < MIN_SCREEN_WIDTH:
            width = MIN_SCREEN_WIDTH
        if height < MIN_SCREEN_HEIGHT:
            height = MIN_SCREEN_HEIGHT
        self.image_size = (width, height)

    def handle_keyboard_events(self, client_socket):
        """
        :param client_socket: the controlled user socket.
        the function handles keyboard events.
        """
        self.client_socket = client_socket
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_listener.start()

    def on_press(self, key):
        """
        :param key: the key that was pressed.
        called when a key was pressed.
        """
        if pygame.mouse.get_focused() == MOUSE_IN_THE_SCREEN_FLAG:
            key_press_command = KeyPress(key)
            self.send_message(key_press_command, True, self.client_socket)
        else:
            self.key_combinations(key)

    def on_release(self, key):
        """
        :param key: the key that was released.
        called when a key was released.
        """
        if pygame.mouse.get_focused() == MOUSE_IN_THE_SCREEN_FLAG:
            key_release_command = KeyRelease(key)
            self.send_message(key_release_command, True, self.client_socket)
        else:
            if any([key in COMBO for COMBO in COPY_KEYBOARD_COMBINATIONS]):
                self.current_key_combinations.remove(key)

    def key_combinations(self, key):
        """
        :param key: the key that was pressed.
        the function checks key combinations and comperes it to the list with the combinations.
        """
        if any([key in COMBO for COMBO in COPY_KEYBOARD_COMBINATIONS]):
            self.current_key_combinations.add(key)
        if any(all(k in self.current_key_combinations for k in COMBO) for COMBO in COPY_KEYBOARD_COMBINATIONS):
            self.send_copied_value()

    def send_copied_value(self):
        """
        the function called when a CTRL + V combination was held and sends the copied value to the controlled user.
        """
        time.sleep(0.1)
        copied_value = clipboard.paste()
        self.send_message(CopyValue(copied_value), True, self.client_socket)
        print 'copied: ' + copied_value


