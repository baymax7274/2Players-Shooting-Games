from src.core.game import Game
from src.scenes.menu import MenuScene

if __name__ == "__main__":
    game = Game()
    game.run(MenuScene(game))
