# -*- coding: utf-8 -*-
class ChatMessage(object):
    def __init__(self, message):
        self.message = message


class FileNotExists(object):
    pass


class DoneSession(object):
    pass


class WrongLoginCreds(object):
    pass


class UserNotExist(object):
    def __init__(self, not_existing_username):
        self.not_existing_username = not_existing_username


class GuestConnection(object):
    """
    Sent to the server in order to start a valid connection
    between the user and the server.
    this object is sent by 'Guest' users, (users who will get random id and password).
    """
    pass


class MemberConnection(object):
    """
    Sent to the server in order to start a valid connection
    between the user and the server.
    this object is sent by 'Members', users who registered to the system.
    * these users will be able to add friends and remember their info.
    """
    def __init__(self, username, password):
        """
        @param username: the user's username.
        @param password: the user's password.
        """
        self.username = username
        self.password = password


class RegisterMessage(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserAlreadyExists(object):
    pass


class SuccessfulLogin(object):
    def __init__(self, user_type):
        self.user_type = user_type


class SuccessfulRegister(object):
    pass


class UserInfo(object):
    def __init__(self, user_type, user_id, password, ip, can_start_session=True):
        """
        @param user_id: the id of the user.
        @param password: the password of the user.
        @param ip: the user's ip address.
        @param can_start_session: a boolean that means of the user can start a control session.
        @param user_type: a string that defines the user type('member' or 'guest')
        """
        self.user_type = user_type
        self.user_id = user_id
        self.password = password
        self.ip = ip
        self.can_start_session = can_start_session

    def change_password(self, new_pass):
        """
        @param new_pass: the new user's password.
        the function changes the user's password.
        """
        self.password = new_pass


class FileMessage(object):
    def __init__(self, file_path):
        """
        @param file_path: the path of the file that is sent(in the sender's machine)
        """
        self.file_path = file_path


class RequestFile(object):
    def __init__(self, file_path):
        """
        @param file_path: the path of the wanted file.
        """
        self.file_path = file_path


class ControlUser(object):
    def __init__(self, remote_user_id, remote_user_password):
        """
        @param remote_user_id: the remote user id (the user you want to control).
        @param remote_user_password: the remote user password (the user you want to control).
        The object is sent when a user wants to control another user.
        """
        self.remote_user_id = remote_user_id
        self.remote_user_password = remote_user_password


class Disconnect(object):
    """
    sent when a user disconnects from the server.
    """
    pass


class WrongCredentials(object):
    pass


class StartConversation(object):
    def __init__(self, role, user_info):
        """
        @param role: defines your role in the remote control conversation
        (controller object or controlled object)

        the message is sent when a remote control 'conversation' starts
        """
        self.role = role
        self.user_info = user_info


class RoleController(object):
    """
    The object is sent when a conversation starts between 2 users
    and defines the user's role in the conversation.
    the user that receives a RoleController object is the controller.
    """
    pass


class RoleControlled(object):
    """
    The object is sent when a conversation starts between 2 users
    and defines the user's role in the conversation.
    the user that receives a RoleControlled object is the controlled.
    """
    pass


class GetID(object):
    def __init__(self, user_id):
        """
        @param user_id: the new id of the user.
        the object is sent to a user so he'll know his id.
        """
        self.user_id = user_id


class GetPassword(object):
    def __init__(self, user_pass):
        """
        @param user_pass: the new password of the user.
        the object is sent to the user so he'll know his password.
        * the server resets the users password every 2 minutes meant a user will get a new instance of the
        object with his new password.
        """
        self.user_password = user_pass


class ScreenResolutionMessage(object):
    def __init__(self, width, height):
        """
        :param width: the width of the controlled user screen resolution(in pixels).
        :param height: the height of the controlled user screen resolution(in pixels).
        sent to the controller so he could make a ratio with the mouse pos of his control screen
        resolution and the resolution of the original screen.
        """
        self.width = width
        self.height = height


class MousePress(object):
    def __init__(self, mouse_click_indicator):
        """
        :param mouse_click_indicator: an int that indicates the mouse press type.
        """
        self.mouse_click_indicator = mouse_click_indicator


class MouseRelease(object):
    def __init__(self, mouse_click_indicator):
        """
        :param mouse_click_indicator: an int that indicated the mouse release type.
        """
        self.mouse_click_indicator = mouse_click_indicator


class MouseScroll(object):
    def __init__(self, mouse_click_indicator):  # TODO DEL THIS CLASS, YOU DON'T NEED IT.
        self.mouse_click_indicator = mouse_click_indicator


class MouseMotion(object):
    def __init__(self, x, y):
        """

        :param x: the new x pos of the mouse.
        :param y: the new y pos of the mouse.
        """
        self.x = x
        self.y = y


class KeyPress(object):
    def __init__(self, key):
        """
        :param key: the key that was pressed.
        """
        self.key = key


class KeyRelease(object):
    def __init__(self, key):
        """
        :param key: the key that was released.
        """
        self.key = key


class ImageSizeChange(object):
    def __init__(self, image_size):
        """
        :param image_size: a dictionary that indicated of the new image size (width, height).
        needed when changing the control screen size.
        """
        self.image_size = image_size


class CopyValue(object):
    def __init__(self, copied_data):
        """
        :param copied_data: the data that was copied in the controller machine.
        when the controller copies something in his pc it copies also at the controlled
        pc.
        """
        self.copied_data = copied_data
