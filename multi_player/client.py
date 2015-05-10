__author__ = 'Harry'
import controllers
import event_manager
import events
import view
import asyncore
import asynchat
import socket
import json
import hashlib

import tkinter
import tkinter.messagebox as messagebox


class Login:
    def __init__(self):
        self._login = tkinter.Tk()
        self._usernameLabel = tkinter.Label(self._login, text = "Username:")
        self._userEntry = tkinter.Entry(self._login)
        self._passwordLabel = tkinter.Label(self._login, text = "Password:")
        self._passEntry = tkinter.Entry(self._login, show="*")
        self._connect = tkinter.Button(self._login, text = "Connect", command = self._connect)
        self._usernameLabel.grid(row = 0, column = 0)
        self._userEntry.grid(row = 0, column = 1)
        self._passwordLabel.grid(row = 1, column = 0)
        self._passEntry.grid(row = 1, column = 1)
        self._connect.grid(row = 2, column = 1)
        
        self._username = ""
        self._password = ""        

        self._login.mainloop()

    def _connect(self):
        self._username = self._userEntry.get()
        self._password = self._passEntry.get()
        
        self._login.destroy()

    def _login_fail(self):
        messagebox.showerror("Error", "Wrong Password!")
        return True

    def get_user(self):
        type(self._username)
        return self._username

    def get_pass(self):
        return self._password

class Client(asynchat.async_chat):

    def __init__(self, host, port, eventManager):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self.set_terminator(b'\n')
        self._received_data = ""
        self._pygame_view = None
        self._login_screen = True
        
    def handle_connect(self):
        print("handle")
        login = Login()
        #self._username = input("Please enter username: ")
        #self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
        self._username = login.get_user()
        self._password = hashlib.sha512(bytes(login.get_pass(), 'UTF-8')).hexdigest()
        print("Hashed Password: {}".format(self._password))
        self.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                                                                ("password", self._password)])) + "\n", 'UTF-8'))

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        self._received_data.strip('\n')
        split_string = self._received_data.split(' ', 1)
        key = split_string[0]
        # print(self._received_data)
        if key == "UPDATE":
            data = split_string[1]
            self._event_manager.post(events.ServerUpdateReceived(data))
        elif key == "LOGIN_REQUEST":
            print("login req")
            login = Login()
            self._username = login.get_user()
            self._password = hashlib.sha512(bytes(login.get_pass(), 'UTF-8')).hexdigest()
        
            #self._username = input("Please enter username: ")
            #self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
            print("Hashed Password: {}".format(self._password))
            self.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                                                                ("password", self._password)])) + "\n", 'UTF-8'))
        elif key == "LOGIN_FAIL":
            print("LOGIN FAILED")
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Error", "Wrong Password!")
            root.destroy()
            login = Login()
            self._username = login.get_user()
            self._password = hashlib.sha512(bytes(login.get_pass(), 'UTF-8')).hexdigest()
            #self._username = input("Please enter username: ")
            #self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
            print("Hashed Password: {}".format(self._password))
            self.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                                                                ("password", self._password)])) + "\n", 'UTF-8'))
        elif key == "LOGIN_SUCCESS":
            print("LOGIN SUCCESSFUL!")
            print("Welcome {}.".format(self._username))
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showinfo("Welcome", "Press OK to start game!")
            root.destroy()
            self._pygame_view = view.PygameView(self._event_manager)
            self.push(bytes("GAME_START\n", 'UTF-8'))
        elif key == "USER_CREATED":
            print("USER CREATED!")
            print("Welcome {}.".format(self._username))
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showinfo("Welcome", "Press OK to start game!")
            root.destroy()
            self._pygame_view = view.PygameView(self._event_manager)
            self.push(bytes("GAME_START\n", 'UTF-8'))
        elif key == "GAME_OVER":
            self._event_manager.post(events.GameOverEvent())
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.push(bytes("QUIT\n",'UTF-8'))
            self.close()
        elif isinstance(event, events.MoveEvent):
            print("Message: {} sent".format(event.get_direction()))
            self.push(bytes("MOVE " + event.get_direction() + "\n", 'UTF-8'))
        elif isinstance(event, events.RestartEvent):
            self.push(bytes("RESTART\n", 'UTF-8'))


def main():
    try:
        eventManager = event_manager.EventManager()
        controller = controllers.Controller(eventManager)
        client = Client('localhost', 8000, eventManager)
        asyncore.loop(timeout=1)
    except:
        pass

if __name__ == "__main__":
    main()
