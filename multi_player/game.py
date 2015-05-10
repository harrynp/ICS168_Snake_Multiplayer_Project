__author__ = 'Harry'
import pygame
import events
from random import randint
import json
import sqlite3 as lite
import hashlib
import base64
import os

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

def print_db():
    with db:
        query.execute("SELECT * FROM Users")
        data = query.fetchall()
        print(data)
    
def update_hscore(USERNAME, H_SCORE):
    with db:
        query.execute("UPDATE Users SET h_score = ? WHERE username = ?", (H_SCORE, USERNAME))

def get_hscore(USERNAME):
    with db:
        query.execute("SELECT h_score FROM Users WHERE username = ?", (USERNAME, ))
        score = query.fetchone()
        return score

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
    def __init__(self, x, y, direction, event_listener):
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

        self._event_listener = event_listener

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


class Game:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._clock = pygame.time.Clock()
        self._snakes = []
        self._snakes.append(Snake(20, 15, "down", self._event_manager))
        #self._snakes.append(Snake(400, 300, "down", self._event_manager))
        self._pellets = []
        self._pellets = [Pellet(randint(1, 39), randint(1, 29))]
        #self._pellets.append(pygame.Rect(randint(2, 53) * 15, randint(2, 39) * 15, 15, 15))
        self._borders = [pygame.Rect(0, 0, 2, 600), pygame.Rect(0, 0, 800, 2), pygame.Rect(798, 0, 2, 600), pygame.Rect(0, 598, 800, 2)]
        self._score = None
        self._is_running = True
        self._game_state = "run"
        # print_db()

    def run(self):
        while self._is_running:
            self._clock.tick(10)
            if self._game_state == "run":
                for snake in self._snakes:
                    if self._collideBorder(snake) or self._collideSelf(snake):
                        self._event_manager.post(events.GameOverEvent())
                    if self._collidePellet(snake):
                        self._spawn_pellet(Pellet(randint(1, 39), randint(1, 29)))
                        self._score.increment_current_score()
                    snake.update()
            self._event_manager.post(events.TickEvent())

    def _spawn_pellet(self, pellet):
        self._pellets.append(pellet)

    def _destroy_pellet(self, pellet):
        self._pellets.remove(pellet)

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
            self._score.save_high_score()
            self._game_state = "game_over"
        elif isinstance(event, events.MoveEvent):
            print(event.get_direction())
            self._snakes[0].change_dir(event.get_direction())
        elif isinstance(event, events.RestartEvent):
            self._snakes.clear()
            self._snakes.append(Snake(20, 15, "down", self._event_manager))
            self._score.reset_score()
            self._game_state = "run"
        elif isinstance(event, events.LoginAttempt):
            enum = login_check(event.get_username(), event.get_password())
            self._score = Score(event.get_username())
            if enum == 0:
                self._event_manager.post(events.LoginFail())
            elif enum == 1:
                self._event_manager.post(events.LoginSuccess())
            elif enum == 2:
                self._event_manager.post(events.UserCreated())

    def get_snakes(self):
        return self._snakes

    def get_pellets(self):
        return self._pellets

    def get_pellets_pos(self):
        pos_list = []
        for pellet in self._pellets:
            pos_list.append(pellet.get_pos())
        return pos_list

    
    def get_score(self):
        return self._score.get_current_score(), self._score.get_high_score()

    def get_game_state(self):
        return self._game_state

    def receive_message(self, message):
        loaded_json = json.loads(message)
        print(json.dumps(loaded_json, sort_keys=True, indent=4))

    def send_update(self):
        json_string = json.dumps(dict([("snakes", self._snakes[0].get_body()),
                                       ("pellets", self.get_pellets_pos()),
                                       ("scores", self._score.get_scores()),
                                       ("game_state", self._game_state)]))
        return json_string
