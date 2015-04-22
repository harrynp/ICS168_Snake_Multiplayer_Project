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
    def __init__(self):
        self._name = "Program Quit Event"


class GameStartedEvent(Event):
    def __init__(self, game):
        self._name = "Game Started Event"
        self._game = game


class GameOverEvent(Event):
    def __init__(self):
        self._name = "Game Over Event"


class MoveEvent(Event):
    def __init__(self, direction):
        self._name = "Move Event"
        self._direction = direction

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