import wx
import wx.lib.scrolledpanel as scrolled
from User import User
from threading import Thread
from Messages import *
from functools import partial
from VideoWriter import VideoWriter


MAIN_FRAME_HEIGHT = 245
MAIN_FRAME_WIDTH = 1000
LOGIN_FRAME_HEIGHT = 285
LOGIN_FRAME_WIDTH = 600
ID_LENGTH = 9
SESSION_PASSWORD_LENGTH = 6
PASSWORD_MIN_LEN = 6
PASSWORD_MAX_LEN = 16
MEMBER_USER_TYPE = 'member'
GUEST_USER_TYPE = 'guest'
ID_LENGTH_ERROR = 'ID must be 9 chars long.'
EMPTY_STRING = ''
RED = '#d10c33'
SELF_MESSAGE_INDICATOR = 'Me> '
FILE_NOT_EXISTS_ERROR = '[!] File does not exists any longer :('
YOUR_MSG_COLOR = (0, 128, 0)  # green
OTHER_MSG_COLOR = (26, 83, 255)  # blue


class MyApp(wx.App):
    def OnInit(self):
        self.user = User()
        self.create_login_frame()
        self.run()
        return True

    def run(self):
        self.user.connect_to_the_server()
        Thread(target=self.user.receive_message).start()

    def create_login_frame(self):
        self.login_frame = LoginFrame(parent=None, title="Bazinga", size=(LOGIN_FRAME_WIDTH, LOGIN_FRAME_HEIGHT),
                               style=wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX)
        self.SetTopWindow(self.login_frame)
        self.login_frame.Show()

    def create_main_frame(self):
        self.frame = MainFrame(parent=None, title="Bazinga", size=(MAIN_FRAME_WIDTH, MAIN_FRAME_HEIGHT),
                               style=wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX)
        self.SetTopWindow(self.frame)
        self.frame.Show()

    def create_chat_frame(self):
        self.chat_frame = ChatFrame(parent=None, title="Bazinga Chat", size=(250, 480),
                      style=wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.CAPTION)
        self.chat_frame.Show()


class LoginFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LoginFrame, self).__init__(*args, **kwargs)
        self.Center()
        self.login_panel = LoginPanel(self)
        self.login_panel.register_btn.Bind(wx.EVT_BUTTON, self.register)
        self.login_panel.guest_login_btn.Bind(wx.EVT_BUTTON, self.guest_login)
        self.login_panel.login_btn.Bind(wx.EVT_BUTTON, self.member_login)

    def set_error(self, error):
        self.login_panel.errors_label.SetLabel(error)

    def guest_login(self, evt):
        connection_message = GuestConnection()
        user = wx.GetApp().user
        user.mess_handler.send_enc_message(connection_message, True, user.client_socket)

    def member_login(self, evt):
        username = self.login_panel.id_input.GetValue()
        password = self.login_panel.password_input.GetValue()
        if self.forms_validation():
            connection_message = MemberConnection(username, password)
            user = wx.GetApp().user
            user.mess_handler.send_enc_message(connection_message, True, user.client_socket)

    def register(self, evt):
        username = self.login_panel.id_input.GetValue()
        password = self.login_panel.password_input.GetValue()
        if self.forms_validation():
            register_message = RegisterMessage(username, password)
            user = wx.GetApp().user
            user.mess_handler.send_enc_message(register_message, True, user.client_socket)

    def forms_validation(self):
        errors = ''
        username = self.login_panel.id_input.GetValue()
        password = self.login_panel.password_input.GetValue()
        if len(username) != ID_LENGTH:
            errors = 'Username must be ' + str(ID_LENGTH) + ' chars long.\n'
        if len(password) < PASSWORD_MIN_LEN or len(password) > PASSWORD_MAX_LEN:
            errors += 'Password must be between ' + str(PASSWORD_MIN_LEN) + ' to ' + str(PASSWORD_MAX_LEN) + ' chars.'

        self.set_error(errors)
        return errors is ''


class LoginPanel(wx.Panel):
    def __init__(self, parent):
        super(LoginPanel, self).__init__(parent)
        self.font = Font(20).font
        self.SetFont(self.font)
        self.create()

    def create(self):
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.id_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.password_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.login_btn_hbox = wx.BoxSizer(wx.HORIZONTAL)

        id_label = wx.StaticText(self, label="Enter ID: ")
        self.id_input = wx.TextCtrl(self, size=(211, -1))
        self.id_input.SetMaxLength(ID_LENGTH)
        self.id_hbox.AddMany([id_label, (91, 0), self.id_input])  # (182, 0),

        password_label = wx.StaticText(self, label="Enter Password: ")
        self.password_input = wx.TextCtrl(self, size=(211, -1), style=wx.TE_PASSWORD)
        self.password_input.SetMaxLength(PASSWORD_MAX_LEN)
        self.password_hbox.AddMany([password_label, (5, 0), self.password_input])  # (96, 0),

        self.login_btn = wx.Button(self, label="Login", size=(150, 50))
        self.guest_login_btn = wx.Button(self, label="Connect as Guest", size=(215, 50))
        self.register_btn = wx.Button(self, label="Register", size=(150, 50))
        self.login_btn_hbox.AddMany([self.register_btn, self.login_btn, self.guest_login_btn])

        self.errors_label = wx.StaticText(self, label='')
        self.errors_label.SetFont(Font(15).font)
        self.errors_label.SetForegroundColour(RED)
        title = wx.StaticText(self, label="Login - Bazinga\n")

        self.vbox.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.Add(self.id_hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.Add(self.password_hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.Add(self.errors_label)
        self.vbox.Add((0, 27))
        self.vbox.Add(self.login_btn_hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizer(self.vbox)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.Center()  # place the window in the center of the screen
        self.menu_bar = None
        self.record_menu = None
        self.record_checkbox = None
        self.status_bar = None
        self.create_frame()
        self.panel = MainPanel(self)
        self.panel.connect_btn.Bind(wx.EVT_BUTTON, self.on_click)
        self.SetSize((820, 245))

    def create_frame(self):
        self.status_bar = self.CreateStatusBar()
        self.menu_bar = wx.MenuBar()
        self.record_menu = wx.Menu()

        self.record_checkbox = self.record_menu.Append(wx.ID_ANY, 'Record Session', 'Make a video of the control session', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_record, self.record_checkbox)
        self.menu_bar.Append(self.record_menu, 'Record Settings')

        self.SetMenuBar(self.menu_bar)

    def toggle_record(self, evt):
        wx.GetApp().user.is_recording = self.record_checkbox.IsChecked()
        print 'Recording Session: ' + str(wx.GetApp().user.is_recording)

    def set_id(self, new_id):
        self.panel.id_label.SetLabel(str(new_id))

    def set_password(self, new_password):
        self.panel.password_label.SetLabel(str(new_password))

    def set_error(self, new_error):
        self.panel.errors_label.SetLabel(str(new_error))

    def on_click(self, event):
        error_string = ''
        if self.panel.tc_id.GetValue() == EMPTY_STRING \
                and self.panel.tc_password.GetValue() == EMPTY_STRING:
            error_string = 'Please Enter ID and Password'
        elif self.panel.tc_password.GetValue() == EMPTY_STRING:
            error_string = 'Please Enter Password'
        elif self.panel.tc_id.GetValue() == EMPTY_STRING:
            error_string = 'Please Enter ID'
        else:
            self.control_user()
        self.panel.errors_label.SetLabel(error_string)

    def control_user(self):
        user_id = self.panel.tc_id.GetValue()
        user_pass = self.panel.tc_password.GetValue()
        control_message = ControlUser(user_id, user_pass)
        user = wx.GetApp().user
        user.mess_handler.send_enc_message(control_message, True, user.client_socket)


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)
        self.font = Font(20).font
        self.SetFont(self.font)
        self.errors_label = wx.StaticText(self, label='')
        self.errors_label.SetFont(Font(16).font)
        self.errors_label.SetForegroundColour(RED)
        self.create()

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        id_hbox = wx.BoxSizer(wx.HORIZONTAL)
        pass_hbox = wx.BoxSizer(wx.HORIZONTAL)

        your_id_label = wx.StaticText(self, label="Your ID: ")
        self.id_label = wx.StaticText(self, label='ID')
        enter_id_label = wx.StaticText(self, label="Enter ID: ")
        self.tc_id = wx.TextCtrl(self, size=(200, -1))
        self.tc_id.SetMaxLength(ID_LENGTH)

        id_hbox.AddMany([your_id_label, self.id_label, (350, -1),
                         enter_id_label, self.tc_id])

        your_password_label = wx.StaticText(self, label="Your Password: ")
        self.password_label = wx.StaticText(self, label='PASSWORD')
        enter_password_label = wx.StaticText(self, label="Enter Password: ")
        self.tc_password = wx.TextCtrl(self, size=(200, -1))
        self.tc_password.SetMaxLength(6)

        pass_hbox.AddMany([your_password_label, self.password_label, (65, -1),
                           enter_password_label, self.tc_password])

        self.connect_btn = wx.Button(self, label="Connect", size=(203, 50))


        vbox.Add(id_hbox, 0, wx.TOP | wx.LEFT, 15)
        vbox.Add(pass_hbox, 0, wx.LEFT, 20)
        vbox.Add(self.connect_btn, 0, wx.LEFT, 599)
        vbox.Add(self.errors_label, 0, wx.ALIGN_CENTER)

        hbox.Add(vbox)
        self.SetSizer(hbox)


class ChatFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatFrame, self).__init__(*args, **kwargs)
        self.create_frame()
        self.main_panel = ChatPanel(self)
        self.main_panel.send_btn.Bind(wx.EVT_BUTTON, self.send_message)
        self.main_panel.msg_input.Bind(wx.EVT_TEXT_ENTER, self.send_message)

    def create_frame(self):
        self.status_bar = self.CreateStatusBar()
        self.menu_bar = wx.MenuBar()
        self.record_menu = wx.Menu()

        self.record_checkbox = self.record_menu.Append(wx.ID_ANY, 'Record Session', 'Make a video of the control session', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_record, self.record_checkbox)
        self.menu_bar.Append(self.record_menu, 'Record Settings')

        user = wx.GetApp().user
        if user.is_recording:
            self.record_checkbox.Check()

        self.SetMenuBar(self.menu_bar)

    def toggle_record(self, evt):
        user_type = wx.GetApp().user.user_type
        user_type.is_recording = not user_type.is_recording
        if user_type.is_recording is False:
            user_type.video_writer.close()
            user_type.video_writer = None
        else:
            user_type.video_writer = VideoWriter()
        print user_type.is_recording

    def send_message(self, evt):
        message = self.main_panel.msg_input.GetValue()
        if message != '':
            client_socket = wx.GetApp().user.user_type.client_socket
            mess_obj = ChatMessage(message)
            wx.GetApp().user.mess_handler.send_enc_message(mess_obj, True, client_socket)
            self.main_panel.msg_input.Clear()
            self.main_panel.chat_log.new_text_message(SELF_MESSAGE_INDICATOR + message, YOUR_MSG_COLOR)

    def send_file(self, file_path):
        if file_path != '':
            client_socket = wx.GetApp().user.user_type.client_socket
            mess_obj = FileMessage(file_path)
            wx.GetApp().user.mess_handler.send_enc_message(mess_obj, True, client_socket)
            self.main_panel.msg_input.Clear()
            file_btn = self.add_file_message(file_path)
            self.main_panel.chat_log.disable_button(file_btn)

    def add_message(self, sender_ip, message):
        try:
            #message = self.decrypt_message(message)
            new_message = sender_ip + '> ' + message
            return self.main_panel.chat_log.new_text_message(new_message, OTHER_MSG_COLOR)
        except RuntimeError:
            pass

    def add_file_message(self, file_path):
        try:
            return self.main_panel.chat_log.new_file_message(file_path)
        except RuntimeError:
            pass


class ChatPanel(wx.Panel):
    def __init__(self, parent):
        super(ChatPanel, self).__init__(parent)
        self.file_drop_target = FileDropTarget(self)
        self.create()

    def create(self):
        self.main_vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.send_btn = wx.Button(self, label='Send', size=(95, 50))
        self.msg_input = wx.TextCtrl(self, size=(150, 50), style=wx.TE_NO_VSCROLL)
        self.chat_log = ChatLogPanel(self, size=(235, 350))

        self.hbox.Add(self.msg_input, 0, wx.LEFT, 5)
        self.hbox.AddMany([(5, -1), self.send_btn])

        self.main_vbox.Add(self.chat_log, 0, wx.LEFT | wx.TOP, 5)
        self.main_vbox.AddMany([(-1, 10), self.hbox])
        self.SetSizer(self.main_vbox)
        self.msg_input.SetDropTarget(self.file_drop_target)


class ChatLogPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, size):
        scrolled.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL, size=size)
        self.files_paths = {}  # button id : file's path
        self.panels = []  # every message is placed in a panel.
        self.button_id = 0
        self.vbox = wx.BoxSizer(wx.VERTICAL)

    def new_text_message(self, message, text_color=None):
        panel = wx.Panel(self)
        panel.SetForegroundColour(text_color)
        if isinstance(message, FileNotExists):
            message = FILE_NOT_EXISTS_ERROR
            panel.SetBackgroundColour(wx.Colour(255, 80, 80))
        wx.StaticText(panel, -1, message)
        self.add_panel_to_list(panel)
        return panel

    def new_file_message(self, file_path):
        panel = wx.Panel(self)
        file_name = file_path[file_path.rfind('\\')+1:]
        file_btn = wx.Button(panel, label=file_name, size=(100, 50), id=self.button_id)
        file_btn.Bind(wx.EVT_BUTTON, partial(self.request_file, btn_id=file_btn.GetId()))
        self.files_paths[self.button_id] = file_path
        self.button_id += 1
        self.add_panel_to_list(panel)
        return file_btn

    @staticmethod
    def disable_button(button):
        button.Disable()

    def add_panel_to_list(self, panel):
        self.panels.append(panel)
        self.vbox.Add(panel)
        self.resetup_panel()

    def request_file(self, evt, btn_id):
        client_socket = wx.GetApp().user.user_type.client_socket
        files_socket = wx.GetApp().user.user_type.files_socket
        file_request_message = RequestFile(self.files_paths[btn_id])
        wx.GetApp().user.mess_handler.send_enc_message(file_request_message, True, client_socket)
        self.recv_thread = Thread(target=wx.GetApp().user.user_type.events_handler.receive_file
               , args=[self.files_paths[btn_id][self.files_paths[btn_id].rfind('.'):], files_socket]).start()
        print self.files_paths[btn_id]

    def resetup_panel(self):
        self.SetSizer(self.vbox)
        self.SetupScrolling(scrollToTop=False)


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        """Constructor"""
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        print filenames
        wx.GetApp().chat_frame.send_file(filenames[0])


class Font(object):
    def __init__(self, font_size):
        self.font = wx.Font(font_size, wx.MODERN,  wx.NORMAL,
                            wx.BOLD, False, 'Calibri Light')


if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
