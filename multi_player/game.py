__author__ = 'Harry'
import pygame
import events


borders = [pygame.Rect(0, 0, 2, 600), pygame.Rect(0, 0, 800, 2), pygame.Rect(798, 0, 2, 600), pygame.Rect(0, 598, 800, 2)]


class Snake:
    def __init__(self, x, y, direction, event_listener):
        self._direction = direction
        self._head = pygame.Rect(x, y, 15, 15)
        self._parts = []
        if direction == "right":
            self._parts.append(pygame.Rect(x - 15, y, 15, 15))
        if direction == "left":
            self._parts.append(pygame.Rect(x + 15, y, 15, 15))
        if direction == "up":
            self._parts.append(pygame.Rect(x, y + 15, 15, 15))
        if direction == "down":
            self._parts.append(pygame.Rect(x, y - 15, 15, 15))
        self._event_listener = event_listener

    def detect_collision(self):
        if self._head.collidelist(borders) != -1:
            self._event_listener.post(events.GameOverEvent())

    def detect_border(self):
        return self._head.collidelist(borders)

    def get_head(self):
        return self._head

    def get_parts(self):
        return self._parts

    def add_part(self):
        if len(self._parts) == 1:
            first_part = self._head
        else:
            first_part = self._parts[len(self._parts) - 2]
        second_part = self._parts[len(self._parts) - 1]
        if first_part.left - second_part.left == 15:
            self._parts.append(pygame.Rect(second_part.left - 15, second_part.top, 15, 15))
        elif first_part.left - second_part.left == -15:
            self._parts.append(pygame.Rect(second_part.left + 15, second_part.top, 15, 15))
        elif first_part.top - second_part.top == 15:
            self._parts.append(pygame.Rect(second_part.left, second_part.top - 15, 15, 15))
        elif first_part.top - second_part.top == -15:
            self._parts.append(pygame.Rect(second_part.left, second_part.top + 15, 15, 15))

    def update(self, direction):
        for i in range(len(self._parts) - 1, -1, -1):
            self._parts[i].left = self._parts[i - 1].left
            self._parts[i].top = self._parts[i - 1].top

        self._parts[0].left = self._head.left
        self._parts[0].top = self._head.top

        if direction != "":
            if not (self._direction == "left" and direction == "right" or self._direction == "right" and direction == "left" or self._direction == "up" and direction == "down" or self._direction == "down" and direction == "up"):
                self._direction = direction

        if self._direction == "right":
            self._head.left += 15
        elif self._direction == "left":
            self._head.left -= 15
        elif self._direction == "up":
            self._head.top -= 15
        elif self._direction == "down":
            self._head.top += 15


class Game:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._clock = pygame.time.Clock()
        self._snakes = []
        self._snakes.append(Snake(400, 300, "down", self._event_manager))
        self._game_state = "run"

    def run(self):
        while self._game_state == "run":
            self._clock.tick(10)
            for snake in self._snakes:
                snake.update("")
                snake.detect_border()
            self._event_manager.post(events.TickEvent())
        while self._game_state == "game over":
            self._clock.tick(10)
            pass

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._game_state = False
        if isinstance(event, events.GameOverEvent):
            self._game_state = "game over"
        if isinstance(event, events.MoveEvent):
            self._snakes[0].update(event.get_direction())

    def get_snakes(self):
        return self._snakes