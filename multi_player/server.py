__author__ = 'Harry'
import game
import event_manager
import events
import asyncore
import asynchat
import threading
import socket


class MessageHandler(asynchat.async_chat):
    def __init__(self, sock, addr, eventManager, game):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self._game = game
        self.set_terminator(b'\n')
        self._received_data = ""

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        # self.push(bytes("Message Received\n", 'UTF-8'))
        print("Message recieved: " + self._received_data)
        self._event_manager.post(events.MoveEvent(self._received_data))
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            data = bytes((self._game.send_update() + "\n"), 'UTF-8')
            self.push(data)


class Server(asyncore.dispatcher):

    def __init__(self, host, port, eventManager, game, game_thread):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        # self.buffer = ""
        self._event_manager = eventManager
        # self._event_manager.register_listener(self)
        self._game = game
        self._game_thread = game_thread

    def handle_accepted(self, sock, addr):
        print("Incoming conection from {}".format(repr(addr)))
        handler = MessageHandler(sock, addr, self._event_manager, self._game)
        self._game_thread.start()


def main():
    eventManager = event_manager.EventManager()
    snake_game = game.Game(eventManager)
    game_thread = threading.Thread(target=snake_game.run, name="Game Thread")
    server = Server('localhost', 8000, eventManager, snake_game, game_thread)
    asyncore.loop(1)

if __name__ == '__main__':
    main()