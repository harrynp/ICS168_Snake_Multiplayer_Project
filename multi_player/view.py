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
        self._font = pygame.font.Font(None, 36)
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
            pellets = self._snake_game.get_pellets()
            score = self._snake_game.get_score()
            snake_surface = pygame.Surface(self._screen.get_size())
            for snake in snakes:
                pygame.draw.rect(snake_surface, white, snake.get_head())
                for segment in snake.get_parts():
                    pygame.draw.rect(snake_surface, white, segment)
            for pellet in pellets:
                pygame.draw.rect(snake_surface, white, pellet)
            score_text = self._font.render("Current Score: " + str(score[0]) + "    High Score: " + str(score[1]), 1, white)
            score_text_pos = score_text.get_rect()
            score_text_pos.centerx = snake_surface.get_rect().centerx
            snake_surface.blit(score_text, score_text_pos)
            if self._snake_game.get_game_state() == "game over":
                game_over_text = self._font.render("Game Over.  Press 'r' to restart or 'q' to quit.", 1, white)
                game_over_text_pos = game_over_text.get_rect()
                game_over_text_pos.centerx = snake_surface.get_rect().centerx
                game_over_text_pos.centery = snake_surface.get_rect().centery
                snake_surface.blit(game_over_text, game_over_text_pos)
            self._screen.blit(snake_surface, (0, 0))
            pygame.display.flip()


