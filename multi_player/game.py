__author__ = 'Harry'
import pygame
import events
from random import randint
import json
import sqlite3 as lite
import hashlib
import base64
import os

class Score:

    def __init__(self, username):
        self._username = username
        self._current_score = 0
        self._high_score = get_hscore(self._username)[0]
        # self._high_score = 0
        self._high_score_changed = False

    def save_high_score(self):
        if self._high_score_changed:
            # update_hscore(self._username, self._current_score)
            pass

    def get_high_score(self):
        return self._high_score

    def get_current_score(self):
        return self._current_score

    def get_scores(self):
        return [self._current_score, self._high_score]

    def increment_current_score(self):
        self._current_score += 1
        if self._current_score > self._high_score:
            self._high_score = self._current_score
            self._high_score_changed = True

    def reset_score(self):
        self._current_score = 0
        self._high_score_changed = False


class Pellet:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        #self._pellet = pygame.Rect(x * 20, y * 20, 20, 20)

    def get_pos(self):
        return (self._x, self._y)

class Snake:
    def __init__(self, x, y, direction):
        self._direction = direction
        self._body = [(x,y)]

        if direction == "right":
            self._body.append((x - 1, y))
        if direction == "left":
            self._body.append((x + 1, y))
        if direction == "up":
            self._body.append((x, y + 1))
        if direction == "down":
            self._body.append((x, y - 1))

        #self._event_listener = event_listener

    def get_head(self):
        return self._body[0]

    def get_body(self):
        return self._body

    def add_part(self, pos):
        self._body.insert(0, pos)

    def change_dir(self, direction):
        if not (self._direction == "left" and direction == "right" or self._direction == "right" and direction == "left" or self._direction == "up" and direction == "down" or self._direction == "down" and direction == "up"):
                self._direction = direction

    def update(self):
                
        if self._direction == "right":
            self._body.insert(0, (self._body[0][0] + 1, self._body[0][1]))
        elif self._direction == "left":
            self._body.insert(0, (self._body[0][0] - 1, self._body[0][1]))
        elif self._direction == "up":
            self._body.insert(0, (self._body[0][0], self._body[0][1] - 1))
        elif self._direction == "down":
            self._body.insert(0, (self._body[0][0], self._body[0][1] + 1))

        self._body.pop()


class Player:
    def __init__(self, name, color):
        #self._pos = pos
        self._name = name
        self._color = color
        self._alive = True

    #def get_pos(self):
    #    return self._pos

    def get_name(self):
        return self._name

    def get_color(self):
        return self._color

    def get_alive(self):
        return self._alive

    def set_alive(self, state):
        self._alive = state


'''POSSIBLE SNAKES
Snake(10, 10, "down")
Snake(10, 30, "left")
Snake(30, 10, "right")
Snake(30, 30, "up")
'''

class Game:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._clock = pygame.time.Clock()
        self._players = []
        self._snakes = []
        self._avail_snakes = [Snake(20, 20, "up"), Snake(10, 20, "right"), Snake(20, 10, "left"), Snake(10, 10, "down")]
        #self._snakes.append(Snake(20, 15, "down"))
        #self._snakes.append(Snake(400, 300, "down", self._event_manager))
        self._pellets = []
        self._pellets = [Pellet(randint(1, 39), randint(1, 29))]
        #self._pellets.append(pygame.Rect(randint(2, 53) * 15, randint(2, 39) * 15, 15, 15))
        self._borders = [pygame.Rect(0, 0, 2, 600), pygame.Rect(0, 0, 800, 2), pygame.Rect(798, 0, 2, 600), pygame.Rect(0, 598, 800, 2)]
        #self._score = None
        self._is_running = True
        self._game_state = "run"
        # print_db()

    def run(self):
        self._spawn_snakes()
        while self._is_running:
            self._clock.tick(10)
            if self._game_state == "run":
                for idx, snake in enumerate(self._snakes):
                    if self._collideBorder(snake) or self._collideSelf(snake):
                        self._players[idx].set_alive(False)
                        #self._event_manager.post(events.GameOverEvent())
                    if self._collidePellet(snake):
                        self._spawn_pellet(Pellet(randint(1, 39), randint(1, 29)))
                        #self._score.increment_current_score()
                    #snake.update()
            self._event_manager.post(events.TickEvent())

    def _add_player(self, name, color):
        self._players.append(Player(name, color))

    def _spawn_pellet(self, pellet):
        self._pellets.append(pellet)

    def _destroy_pellet(self, pellet):
        self._pellets.remove(pellet)

    def _spawn_snakes(self):
        for player in self._players:
            self._snakes.append(self._avail_snakes.pop())

    def _collidePellet(self, snake):
        for pellet in self._pellets:
            if snake.get_head() == pellet.get_pos():
                snake.add_part(pellet.get_pos())
                self._destroy_pellet(pellet)
                return True
        return False

    def _collideBorder(self, snake):
        x = snake.get_head()[0]
        y = snake.get_head()[1]
        if x < 0 or x > 39 or y < 0 or y > 29:
            return True
        return False

    def _collideSelf(self, snake):  
        for segment in snake.get_body()[1:]:
            if segment == snake.get_head():
                return True
        return False

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._is_running = False
        elif isinstance(event, events.GameOverEvent):
            #self._score.save_high_score()
            self._game_state = "game_over"
        elif isinstance(event, events.MoveEvent):
            for idx, player in enumerate(self._players):
                name = player.get_name()
                if player.get_name() == event.get_username():
                    self._snakes[idx].change_dir(event.get_direction())
                    self._snakes[idx].update()
        elif isinstance(event, events.RestartEvent):
            self._snakes.clear()
            self._snakes.append(Snake(20, 15, "down"))
            #self._score.reset_score()
            self._game_state = "run"
            
        elif isinstance(event, events.JoinEvent):
            self._add_player(event.get_username(), event.get_color())

    def get_snakes(self):
        return self._snakes

    def get_pellets(self):
        return self._pellets

    def get_pellets_pos(self):
        pos_list = []
        for pellet in self._pellets:
            pos_list.append(pellet.get_pos())
        return pos_list

    
    #def get_score(self):
    #    return self._score.get_current_score(), self._score.get_high_score()

    def get_game_state(self):
        return self._game_state

    def receive_message(self, message):
        loaded_json = json.loads(message)
        print(json.dumps(loaded_json, sort_keys=True, indent=4))

    def send_update(self):
        snake_list = []
        for snake in self._snakes:
            snake_list.append(snake.get_body())
        json_string = json.dumps(dict([("snakes", snake_list),
                                       ("pellets", self.get_pellets_pos()),
                                       #("scores", self._score.get_scores()),
                                       ("game_state", self._game_state)]))
        return json_string
