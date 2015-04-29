__author__ = 'Harry'
import game
import event_manager
import events
import asyncore
import asynchat
import threading
import socket
import json


class MessageHandler(asynchat.async_chat):
    def __init__(self, sock, addr, eventManager, game, game_thread):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self._game = game
        self._game_thread = game_thread
        self.set_terminator(b'\n')
        self._received_data = ""

    # def handle_close(self):
    #     self._event_manager.post(events.QuitEvent())

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        self._received_data = self._received_data.strip('\n')
        split_string = self._received_data.split(' ', 1)
        key = split_string[0]
        if key == "LOGIN_ATTEMPT":
            data = split_string[1]
            json_data = json.loads(data)
            self._event_manager.post(events.LoginAttempt(json_data["username"], json_data["password"]))
        elif key == "MOVE":
            data = split_string[1]
            self._event_manager.post(events.MoveEvent(data))
        elif key == "GAME_START":
            self._game_thread.start()
        elif key == "QUIT":
            self._event_manager.post(events.QuitEvent())
        elif key == "RESTART":
            self._event_manager.post(events.RestartEvent())
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            data = bytes(("UPDATE " + self._game.send_update() + "\n"), 'UTF-8')
            self.push(data)
        elif isinstance(event, events.LoginRequest):
            self.push(bytes("LOGIN_REQUEST\n", 'UTF-8'))
        elif isinstance(event, events.LoginFail):
            self.push(bytes("LOGIN_FAIL\n", 'UTF-8'))
        elif isinstance(event, events.LoginSuccess):
            self.push(bytes("LOGIN_SUCCESS\n", 'UTF-8'))
        elif isinstance(event, events.UserCreated):
            self.push(bytes("USER_CREATED\n", 'UTF-8'))
        elif isinstance(event, events.GameOverEvent):
            self.push(bytes("GAME_OVER\n", 'UTF-8'))


class Server(asyncore.dispatcher):

    def __init__(self, host, port, eventManager, game, game_thread):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self._event_manager = eventManager
        self._game = game
        self._game_thread = game_thread

    def handle_accepted(self, sock, addr):
        print("Incoming conection from {}".format(repr(addr)))
        handler = MessageHandler(sock, addr, self._event_manager, self._game, self._game_thread)


def main():
    try:
        eventManager = event_manager.EventManager()
        snake_game = game.Game(eventManager)
        game_thread = threading.Thread(target=snake_game.run, name="Game Thread")
        server = Server('localhost', 8000, eventManager, snake_game, game_thread)
        asyncore.loop(1)
    except:
        pass


if __name__ == '__main__':
    main()