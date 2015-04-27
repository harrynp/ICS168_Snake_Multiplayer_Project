__author__ = 'Harry'
import game
import event_manager
import events
import asyncore
import asynchat
import threading
import socket


class MessageHandler(asynchat.async_chat):
    def __init__(self, sock, addr, eventManager):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self._event_manager = eventManager
        self.set_terminator("\n")
        self._recieved_data = ""

    def collect_incoming_data(self, data):
        self._recieved_data += data

    def found_terminator(self):
        self.push("Message Recieved\n")
        self._event_manager.post(events.MoveEvent(self._recieved_data))
        self._recieved_data = ""

    # def handle_read(self):
    #     data = self.recv(8192)
    #     if data:
    #         self.send("Move recieved")


class Server(asyncore.dispatcher):

    def __init__(self, host, port, eventManager, game, game_thread):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.buffer = ""
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self._game = game
        self._game_thread = game_thread

    def handle_accepted(self, sock, addr):
        print("Incoming conection from {}".format(repr(addr)))
        handler = MessageHandler(sock, addr, self._event_manager)
        # self._game_thread.start()


    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            self.send(self._game.send_update() + "\n")


def main():
    eventManager = event_manager.EventManager()
    snake_game = game.Game(eventManager)
    game_thread = threading.Thread(target=snake_game.run, name="Game Thread")
    server = Server('localhost', 8000, eventManager, game, game_thread)
    asyncore.loop(1)

if __name__ == '__main__':
    main()