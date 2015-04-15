__author__ = 'Harry'
import pygame
from random import randint

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake")
black = (0, 0, 0)
white = (255, 255, 255)
clock = pygame.time.Clock()
borders = [pygame.Rect(0, 0, 2, 600), pygame.Rect(0, 0, 800, 2), pygame.Rect(798, 0, 2, 600), pygame.Rect(0, 598, 800, 2)]
font = pygame.font.Font(None, 36)
gameLoop = True


class Score:

    def __init__(self, high_score_file):
        self._high_score_file = high_score_file
        self._current_score = 0
        self._high_score = 0
        self._high_score_changed = False
        try:
            high_score_file = open(self._high_score_file, "r")
            self._high_score = int(high_score_file.read())
            high_score_file.close()
        except IOError:
            print("No High Score found, Starting at 0")
        except ValueError:
            print("High Score file is not an int, starting at 0")

    def save_high_score(self):
        if self._high_score_changed:
            try:
                high_score_file = open(self._high_score_file, "w")
                high_score_file.write(str(self._high_score))
                high_score_file.close()
                self._high_score = self._current_score
            except IOError:
                print("Unable to save high score.")

    def get_high_score(self):
        return self._high_score

    def get_current_score(self):
        return self._current_score

    def increment_current_score(self):
        self._current_score += 1
        if self._current_score > self._high_score:
            self._high_score = self._current_score
            self._high_score_changed = True

    def reset_score(self):
        self._current_score = 0
        self._high_score_changed = False


class Snake:

    def __init__(self, x, y, direction):
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

    def detect_collision(self):
        return self._head.collidelist(self._parts)

    def detect_border(self):
        return self._head.collidelist(borders)

    def get_head(self):
        return self._head

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
            self._direction = direction

        if self._direction == "right":
            self._head.left += 15
        elif self._direction == "left":
            self._head.left -= 15
        elif self._direction == "up":
            self._head.top -= 15
        elif self._direction == "down":
            self._head.top += 15

    def render(self):
        pygame.draw.rect(screen, white, self._head)
        for segment in self._parts:
            pygame.draw.rect(screen, white, segment)

snake = Snake(400, 300, "down")
pellet = pygame.Rect(randint(10, 790), randint(10, 590), 15, 15)
score = Score("high_score.txt")

while gameLoop:
    for border in borders:
        pygame.draw.rect(screen, white, border)
    move = ""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameLoop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move = "left"
            if event.key == pygame.K_RIGHT:
                move = "right"
            if event.key == pygame.K_UP:
                move = "up"
            if event.key == pygame.K_DOWN:
                move = "down"
    screen.fill(black)
    snake.update(move)
    snake.render()
    pygame.draw.rect(screen, white, pellet)
    score_text = font.render("Current Score: " + str(score.get_current_score()) + "    High Score: " + str(score.get_high_score()), 1, white)
    score_text_pos = score_text.get_rect()
    score_text_pos.centerx = screen.get_rect().centerx
    screen.blit(score_text, score_text_pos)
    pygame.display.flip()
    clock.tick(5)
    if snake.detect_collision() != -1 or snake.detect_border() != -1:
        gameOverLoop = True
        score.save_high_score()
        game_over_text = font.render("Game Over.  Press 'r' to restart or 'q' to quit.", 1, white)
        game_over_text_pos = game_over_text.get_rect()
        game_over_text_pos.centerx = screen.get_rect().centerx
        game_over_text_pos.centery = screen.get_rect().centery
        screen.blit(game_over_text, game_over_text_pos)
        while gameOverLoop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameLoop = False
                    gameOverLoop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        snake = Snake(400, 300, "down")
                        pellet = pygame.Rect(randint(10, 790), randint(10, 590), 15, 15)
                        score.reset_score()
                        gameOverLoop = False
                    if event.key == pygame.K_q:
                        gameLoop = False
                        gameOverLoop = False
            pygame.display.flip()
    if snake.get_head().colliderect(pellet):
        snake.add_part()
        pellet = pygame.Rect(randint(10, 790), randint(10, 590), 15, 15)
        score.increment_current_score()

score.save_high_score()
pygame.quit()