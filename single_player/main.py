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
    pygame.display.flip()
    clock.tick(5)
    temp = snake.detect_collision()
    if snake.detect_collision() != -1 or snake.detect_border() != -1:
        gameOverLoop = True
        snake.render()
        text = font.render("Game Over.  Press 'r' to restart or 'q' to quit.", 1, white)
        textpos = text.get_rect()
        textpos.centerx = screen.get_rect().centerx
        textpos.centery = screen.get_rect().centery
        screen.blit(text, textpos)
        while gameOverLoop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameLoop = False
                    gameOverLoop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        snake = Snake(400, 300, "down")
                        pellet = pygame.Rect(randint(10, 790), randint(10, 590), 15, 15)
                        gameOverLoop = False
                    if event.key == pygame.K_q:
                        gameLoop = False
                        gameOverLoop = False
            pygame.display.flip()
    if snake.get_head().colliderect(pellet):
        snake.add_part()
        pellet = pygame.Rect(randint(10, 790), randint(10, 590), 15, 15)

pygame.quit()