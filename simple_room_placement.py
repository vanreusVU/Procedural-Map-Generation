# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles

class SimpleRoomPlacement(RogueLikeDefaults):
    ''' Simple Room Placement Algorithm for random dungeon generation'''
    def __init__(self):
        RogueLikeDefaults.__init__(self,
            height=10,
            width=10,
            grid_size=40,
            fps=5)

        self.tiles[9][9] = Tiles.PATH

    def update(self):
        pass
        
            

def main():
    srp = SimpleRoomPlacement()
    srp.start()

if __name__ == "__main__":
    main()