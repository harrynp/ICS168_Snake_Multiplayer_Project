__author__ = 'Harry'
import controllers
import event_manager
import events
import view
import asyncore
import socket


class Client(asyncore.dispatcher):

    def __init__(self, host, port, event_manager):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.buffer = ""
        self._event_manager = event_manager
        self._event_manager.register_listener(self)

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        self._event_manager.post(events.ServerUpdateRecieved(self.recv(8192)))

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.close()
        elif isinstance(event, events.MoveEvent):
            self.buffer = event.get_direction()

def main():
    eventManager = event_manager.EventManager()
    controller = controllers.Controller(eventManager)
    # pygameView = view.PygameView(eventManager, snake_game)
    client = Client('localhost', 8000, eventManager)
    asyncore.loop(timeout=1)

if __name__ == "__main__":
    main()