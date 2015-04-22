__author__ = 'Harry'
import pygame
import events
import game

black = (0, 0, 0)
white = (255, 255, 255)


class PygameView:

    def __init__(self, event_manager, snake_game):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._snake_game = snake_game
        pygame.init()
        self._screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Snake")
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(black)
        self._screen.blit(self._background, (0, 0))
        pygame.display.flip()

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            #Draw Everything
            self._screen.blit(self._background, (0, 0))
            snakes = self._snake_game.get_snakes()
            snake_surface = pygame.Surface(self._screen.get_size())
            for snake in snakes:
                pygame.draw.rect(snake_surface, white, snake.get_head())
                for segment in snake.get_parts():
                    pygame.draw.rect(snake_surface, white, segment)
            self._screen.blit(snake_surface, (0,0))
            pygame.display.flip()


