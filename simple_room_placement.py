# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles

class SimpleRoomPlacement(RogueLikeDefaults):
    def __init__(self):
        RogueLikeDefaults.__init__(self,
            height=10,
            width=10,
            grid_size=40,
            fps=5)

        self.tiles[1][2] = Tiles.PATH

    def drawDungeon(self):
        pass
        # self.drawRectangle()
        
            

def main():
    srp = SimpleRoomPlacement()
    srp.start()

if __name__ == "__main__":
    main()