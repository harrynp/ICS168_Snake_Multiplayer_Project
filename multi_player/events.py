__author__ = 'Harry'


class Event:
    """Superclass for any event from an object that is sent to the EventManager"""
    def __init__(self):
        self._name = "Generic Event"

    def get_name(self):
        return self._name


class TickEvent(Event):
    def __init__(self):
        self._name = "CPU Tick Event"


class QuitEvent(Event):
    def __init__(self, username):
        self._name = "Program Quit Event"
        self._username = username

    def get_username(self):
        return self._username


class GameStartedEvent(Event):
    def __init__(self, game):
        self._name = "Game Started Event"
        self._game = game


class GameOverEvent(Event):
    def __init__(self):
        self._name = "Game Over Event"


class MoveEvent(Event):
    def __init__(self, username, direction):
        self._name = "Move Event"
        self._username = username
        self._direction = direction

    def get_username(self):
        return self._username

    def get_direction(self):
        return self._direction

class MouseEvent(Event):
    def __init__(self, position):
        self._name = "Mouse Event"
        self._position = position

    def get_position(self):
        return self._position


class RestartEvent(Event):
    def __init__(self):
        self._name = "Restart Event"


class ServerUpdateReceived(Event):
    def __init__(self, json_string):
        self._name = "Server Update Received"
        self._json_string = json_string

    def get_json_string(self):
        return self._json_string


class LoginRequest(Event):
    def __init__(self):
        self._name = "Login Request"


# class LoginAttempt(Event):
#     def __init__(self, username, password):
#         self._name = "Login Attempt"
#         self._username = username
#         self._password = password
#
#     def get_username(self):
#         return self._username
#
#     def get_password(self):
#         return self._password


class LoginSuccess(Event):
    def __init__(self):
        self._name = "Login Success"


class LoginFail(Event):
    def __init__(self):
        self._name = "Login Fail"

class UserCreated(Event):
    def __init__(self):
        self._name = "User Created"


class GameStart(Event):
    def __init__(self):
        self._name = "Game Start"

class JoinEvent(Event):
    def __init__(self, username, color):
        self._name = "Join Event"
        self._username = username
        self._color = color

    def get_username(self):
        return self._username

    def get_color(self):
        return self._color

class LeaveGame(Event):
    def __init__(self, username):
        self._name = "Leave Game"
        self._username = username

    def get_username(self):
        return self._username

class GameFull(Event):
    def __init__(self):
        self._name = "Game Full"

class GameJoined(Event):
    def __init__(self):
        self._name = "Game Joined"