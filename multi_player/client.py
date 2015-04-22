__author__ = 'Harry'
import controllers
import event_manager
import view
import game


def main():
    eventManager = event_manager.EventManager()
    controller = controllers.Controller(eventManager)
    snake_game = game.Game(eventManager)
    pygameView = view.PygameView(eventManager, snake_game)
    snake_game.run()


if __name__ == "__main__":
    main()