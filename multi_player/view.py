__author__ = 'Harry'
import pygame
import events
import json

black = (0, 0, 0)
white = (255, 255, 255)

class PygameView:

    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        pygame.init()
        self._font = pygame.font.Font(None, 36)
        self._screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Snake")
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(black)
        self._screen.blit(self._background, (0, 0))
        pygame.display.flip()

    def notify(self, event):
        if isinstance(event, events.ServerUpdateReceived):
            #Draw Everything
            self._screen.blit(self._background, (0, 0))
            game_data = json.loads(event.get_json_string())
            snakes = game_data["snakes"]
            pellets = game_data["pellets"]
            scores = game_data["scores"]
            game_state = game_data["game_state"]
            snake_surface = pygame.Surface(self._screen.get_size())
            for part in snakes:
                snake_part = pygame.Rect(part[0]*20, part[1]*20, 20, 20)
                pygame.draw.rect(snake_surface, white, snake_part)
            for pellet in pellets:
                pygame.draw.circle(snake_surface, white, (pellet[0] * 20 + 10, pellet[1] * 20 + 10), 5)
                #p = pygame.Rect(pellet[0], pellet[1], 15, 15)
                #pygame.draw.rect(snake_surface, white, p)
            score_text = self._font.render("Current Score: " + str(scores[0]) + "    High Score: " + str(scores[1]), 1, white)
            score_text_pos = score_text.get_rect()
            score_text_pos.centerx = snake_surface.get_rect().centerx
            snake_surface.blit(score_text, score_text_pos)
            if game_state == "game_over":
                game_over_text = self._font.render("Game Over.  Press 'r' to restart or 'q' to quit.", 1, white)
                game_over_text_pos = game_over_text.get_rect()
                game_over_text_pos.centerx = snake_surface.get_rect().centerx
                game_over_text_pos.centery = snake_surface.get_rect().centery
                snake_surface.blit(game_over_text, game_over_text_pos)
            self._screen.blit(snake_surface, (0, 0))
            pygame.display.flip()
        elif isinstance(event, events.QuitEvent):
            pygame.display.quit()