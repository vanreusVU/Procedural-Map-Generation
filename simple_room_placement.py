# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles
from dungeon_parts import Room

class SimpleRoomPlacement(RogueLikeDefaults):
    ''' Simple Room Placement Algorithm for random dungeon generation'''
    def __init__(self):
        RogueLikeDefaults.__init__(self,
            height=50,
            width=50,
            grid_size=20,
            fps=1)

        # TODO: Test, remove later
        # self.dungeon_parts.append(Room(1,1,5,5))

    def update(self):
        print("hello")
        pass
        
def main():
    srp = SimpleRoomPlacement()
    srp.start()

if __name__ == "__main__":
    main()