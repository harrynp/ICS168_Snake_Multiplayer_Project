__author__ = 'Harry'
import game
import event_manager
import events
import asyncore
import asynchat
import threading
import socket
import json
import sqlite3 as lite
import hashlib
import base64
import os
import traceback

clients = {}
game_sessions = {}

db = lite.connect('login.db')
query = db.cursor()


def login_check(username, password):
    """return 0 if username is in database/pass incorrect, 1 if info correct, 2 is username not in db"""
    #with is like a fancy 'try+catch' for db
    with db:
        # query.execute("CREATE TABLE IF NOT EXISTS Users(username TEXT, password TEXT, h_score INT)")
        query.execute("CREATE TABLE IF NOT EXISTS Users(username TEXT, hash TEXT, salt TEXT, h_score INT)")
        #check if username exists in db
        query.execute("SELECT * FROM Users WHERE username = ?", (username, ))
        check=query.fetchone()
        print("Login attempt from USERNAME: {}".format(password))
        # print_db()

        #if username does not exist, add to users table in db
        if check is None:
            print("Username does not exist")
            #code below inserts the new user into db
            salt = base64.b64encode(os.urandom(128)).decode('UTF-8')
            hashed_password = hashlib.sha512(bytes(password + salt, 'UTF-8')).hexdigest()
            query.execute("INSERT INTO Users VALUES(?, ?, ?, ?)", (username, hashed_password, salt, 0))
            # print_db()
            return 2
        else:
            #if username exists, check if pass correct
            query.execute("SELECT salt FROM Users WHERE username = ?", (username, ))
            salt = query.fetchone()[0]
            hashed_password = hashlib.sha512(bytes(password + salt, 'UTF-8')).hexdigest()
            query.execute("SELECT * FROM Users WHERE username = ? AND hash = ?", (username, hashed_password, ))
            check=query.fetchone()

            #if wrong password
            if check is None:
                print("Hashed password: {}".format(hashed_password))
                print("Wrong password")
                return 0
            #else success
            else:
                print("Hashed password: {}".format(hashed_password))
                return 1


class MessageHandler(asynchat.async_chat):
    def __init__(self, sock, addr, game_sessions):
        asynchat.async_chat.__init__(self, sock=sock, map=clients)
        self._event_manager = None
        self._game_sessions = game_sessions
        self.set_terminator(b'\n')
        self._username = ""
        self._game_id = None
        self._game_thread = None
        self._received_data = ""

    def handle_close(self):
        # self._event_manager.post(events.LeaveGame(self._username))
        pass

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        self._received_data = self._received_data.strip('\n')
        split_string = self._received_data.split(' ', 1)
        key = split_string[0]
        print(self._received_data)
        if key == "LOGIN_ATTEMPT":
            data = split_string[1]
            json_data = json.loads(data)
            enum = login_check(json_data["username"], json_data["password"])
            if enum == 0:
                self.push(bytes("LOGIN_FAIL\n", 'UTF-8'))
            elif enum == 1:
                self._username = json_data["username"]
                self.push(bytes("LOGIN_SUCCESS\n", 'UTF-8'))
            elif enum == 2:
                self._username = json_data["username"]
                self.push(bytes("USER_CREATED\n", 'UTF-8'))

        elif key == "MOVE":
            data = split_string[1]
            json_data = json.loads(data)
            self._event_manager.post(events.MoveEvent(json_data["username"], json_data["direction"]))
            print(json_data["username"] + ": " + json_data["direction"])
        elif key == "NEW_GAME":
            self._game_id = self._username
            self._event_manager = event_manager.EventManager()
            self._event_manager.register_listener(self)
            self._game_sessions[self._game_id] = dict([("game", game.Game(self._event_manager)),
                                                       ("clients", [self]),
                                                       ("event_manager", self._event_manager)])
            self._game_thread = threading.Thread(target=self._game_sessions[self._game_id]["game"].run)
            self._event_manager.post(events.JoinEvent(self._username, "red"))
        elif key == "JOIN_GAME":
            data = split_string[1]
            print(data)
            # json_data = json.loads(data)
            self._game_id = data
            self._game_sessions[data]["clients"].append(self)
            self._event_manager = self._game_sessions[data]["event_manager"]
            self._event_manager.register_listener(self)
            self._event_manager.post(events.JoinEvent(self._username, "blue"))
        elif key == "GAME_START":
            self._game_thread.start()
        elif key == "QUIT":
            self._event_manager.post(events.QuitEvent())
        elif key == "RESTART":
            self._event_manager.post(events.RestartEvent())
        self._received_data = ""

    def get_username(self):
        return self._username

    def handle_error(self):
        '''Handle any uncaptured error in the core. Overrides asyncore's handle_error
        This prevents the server from disconnecting when it use to send something twice
        and then disconnect.'''
        trace = traceback.format_exc()
        try:
            print(trace)
        except Exception as e:
            print('Uncaptured error!' + e)

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            try:
                data = bytes(("UPDATE " + self._game_sessions[self._game_id]["game"].send_update() + "\n"), 'UTF-8')
                for client in self._game_sessions[self._game_id]["clients"]:
                    client.push(data)
            except:
                pass
        # elif isinstance(event, events.LoginRequest):
        #     self.push(bytes("LOGIN_REQUEST\n", 'UTF-8'))
        # elif isinstance(event, events.LoginFail):
        #     self.push(bytes("LOGIN_FAIL\n", 'UTF-8'))
        # elif isinstance(event, events.LoginSuccess):
        #     self.push(bytes("LOGIN_SUCCESS\n", 'UTF-8'))
        # elif isinstance(event, events.UserCreated):
        #     self.push(bytes("USER_CREATED\n", 'UTF-8'))
        elif isinstance(event, events.GameFull):
            self.push(bytes("GAME_FULL\n", 'UTF-8'))
        elif isinstance(event, events.GameJoined):
            self.push(bytes("GAME_JOINED\n", 'UTF-8'))
        elif isinstance(event, events.GameOverEvent):
            self.push(bytes("GAME_OVER\n", 'UTF-8'))


class Server(asyncore.dispatcher):

    def __init__(self, host, port, game_sessions):
        asyncore.dispatcher.__init__(self, map=clients)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self._game_sessions = game_sessions
        print("Server started.")
        print("Waiting for connections...")

    def handle_accepted(self, sock, addr):
        print("Incoming conection from {}".format(repr(addr)))
        handler = MessageHandler(sock, addr, self._game_sessions)


def main():
    eventManager = event_manager.EventManager()
    server = Server('localhost', 8000, game_sessions)
    asyncore.loop(timeout=1, map=clients)



if __name__ == '__main__':
    main()
