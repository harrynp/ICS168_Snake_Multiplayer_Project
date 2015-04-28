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


# class Client(asyncore.dispatcher):
#
#     def __init__(self, host, port, eventManager, pygameView):
#         asyncore.dispatcher.__init__(self)
#         self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.connect((host, port))
#         self.buffer = ""
#         self._event_manager = eventManager
#         self._event_manager.register_listener(self)
#         self._pyagame_view = pygameView
#
#     def handle_connect(self):
#         pass
#
#     def handle_close(self):
#         self.close()
#
#     def handle_read(self):
#         self._event_manager.post(events.ServerUpdateRecieved(self.recv(8192)))
#
#     def writable(self):
#         return len(self.buffer) > 0
#
#     def handle_write(self):
#         sent = self.send(self.buffer)
#         self.buffer = self.buffer[sent:]
#
#     def notify(self, event):
#         if isinstance(event, events.QuitEvent):
#             self.close()
#         elif isinstance(event, events.MoveEvent):
#             self.buffer = event.get_direction()

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
        self._username = ""
        self._password = ""

    def handle_connect(self):
            self._username = input("Please enter username: ")
            self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
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
            self._username = input("Please enter username: ")
            self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
            self.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                                                                ("password", self._password)])) + "\n", 'UTF-8'))
        elif key == "LOGIN_FAIL":
            print("LOGIN FAILED")
            self._username = input("Please enter username: ")
            self._password = hashlib.sha512(bytes(input("Please enter password: "), 'UTF-8')).hexdigest()
            self.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                                                                ("password", self._password)])) + "\n", 'UTF-8'))
        elif key == "LOGIN_SUCCESS":
            print("LOGIN SUCCESSFUL!")
            print("Welcome {}.".format(self._username))
            input("Press any key to start.")
            self._pygame_view = view.PygameView(self._event_manager)
            self.push(bytes("GAME_START\n", 'UTF-8'))
        elif key == "USER_CREATED":
            print("USER CREATED!")
            print("Welcome {}.".format(self._username))
            input("Press any key to start.")
            self._pygame_view = view.PygameView(self._event_manager)
            self.push(bytes("GAME_START\n", 'UTF-8'))
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.close()
        elif isinstance(event, events.MoveEvent):
            print("Message: {} sent".format(event.get_direction()))
            self.push(bytes("MOVE " + event.get_direction() + "\n", 'UTF-8'))


def main():
    eventManager = event_manager.EventManager()
    controller = controllers.Controller(eventManager)
    client = Client('localhost', 8000, eventManager)
    asyncore.loop(timeout=1)

if __name__ == "__main__":
    main()