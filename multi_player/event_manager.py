__author__ = 'Harry'
import events

class EventManager:
    """Coordinates communication between the MVC (Model View Controller)"""
    def __init__(self):
        from weakref import  WeakKeyDictionary
        self._listeners = WeakKeyDictionary()
        self._eventQueue = []

    def register_listener(self, listener):
        self._listeners[listener] = 1

    def unregister_listener(self, listener):
        del self._listeners[listener]

    def post(self, event):
        """Broadcast event to all listeners"""
        if not isinstance(event, events.TickEvent):
            print("Message: " + event.get_name())
            if isinstance(event, events.MouseEvent):
                print(event.get_position())
            elif isinstance(event, events.MoveEvent):
                print(event.get_direction())
        for listener in self._listeners.keys():
            listener.notify(event)