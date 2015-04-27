__author__ = 'Harry'
import controllers
import event_manager
import events
import view
import asyncore
import asynchat
import socket


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

    def __init__(self, host, port, eventManager, pygameView):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self.set_terminator(b'\n')
        self._received_data = ""
        self._pygame_view = pygameView

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        self._event_manager.post(events.ServerUpdateReceived(self._received_data.strip('\n')))
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.close()
        elif isinstance(event, events.MoveEvent):
            print("Message: {} sent".format(event.get_direction()))
            self.push(bytes(event.get_direction() + "\n", 'UTF-8'))


def main():
    eventManager = event_manager.EventManager()
    controller = controllers.Controller(eventManager)
    pygameView = view.PygameView(eventManager)
    client = Client('localhost', 8000, eventManager, pygameView)
    asyncore.loop(timeout=1)

if __name__ == "__main__":
    main()