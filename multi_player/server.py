__author__ = 'Harry'
import game
import event_manager
import events
import asyncore
import threading
import socket


class MessageHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.send("Move recieved")


class Server(asyncore.dispatcher):

    def __init__(self, host, port, eventManager, game):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.buffer = ""
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self._game = game

    def handle_accepted(self, sock, addr):
        print("Incoming conection from {}".format(repr(addr)))
        handler = MessageHandler(sock)

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            self.send(self._game.send_update())


def main():
    eventManager = event_manager.EventManager()
    snake_game = game.Game(eventManager)
    server = Server('localhost', 8000, eventManager, snake_game)
    asyncore.loop(1)

if __name__ == '__main__':
    main()