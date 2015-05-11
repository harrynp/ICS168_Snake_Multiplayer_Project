__author__ = 'Harry'
import events
import pygame


class Controller:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._game_state = "run"

    def notify(self, event):
        e = None
        if isinstance(event, events.GameOverEvent):
            self._game_state = "game_over"
        elif isinstance(event, events.ServerUpdateReceived):
            if self._game_state == "run":
                # Handles input events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        e = events.QuitEvent()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            e = events.MoveEvent("", "left")
                        elif event.key == pygame.K_RIGHT:
                            e = events.MoveEvent("", "right")
                        elif event.key == pygame.K_UP:
                            e = events.MoveEvent("", "up")
                        elif event.key == pygame.K_DOWN:
                            e = events.MoveEvent("", "down")
                        # elif event.key == pygame.K_q:
                        #     e = events.QuitEvent()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            e = events.MouseEvent(event.pos)
            elif self._game_state == "game_over":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        e = events.QuitEvent()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            e = events.RestartEvent()
                            self._game_state = "run"
                        elif event.key == pygame.K_q:
                            e = events.QuitEvent()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            e = events.MouseEvent(event.pos)
        if e:
            self._event_manager.post(e)

