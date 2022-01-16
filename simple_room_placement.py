# Default Modules
from turtle import width
from typing import List
from random import randint, randrange

# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles
from dungeon_parts import CustomRoom, DungeonPart, Room

# ROOM CREATION CONSTANTS (inclusive)
# WIDTH
MIN_ROOM_WIDTH = 3
MAX_ROOM_WIDTH = 5

# HEIGHT
MIN_ROOM_HEIGHT = 3
MAX_ROOM_HEIGHT = 5

# DOOR NUM
MIN_ROOM_DOOR = 1
MAX_ROOM_DOOR = 2

class SimpleRoomPlacement(RogueLikeDefaults):
    '''Simple Room Placement Algorithm for random dungeon generation'''
    
    

    def __init__(self, num_rooms: int = 0, custom_rooms: List[CustomRoom] = []):
        '''
        @num_rooms: number of randomly generated rooms to create and place on the map.
        if set, will ignore @custom_rooms
        @custom_rooms: custom rooms to place on the map
        '''

        RogueLikeDefaults.__init__(self,
            height=20,
            width=20,
            grid_size=40,
            fps=10)

        # Setting up room settings
        self.num_rooms = num_rooms
        self.custom_rooms = custom_rooms

    def canPlace(self, part_to_place: DungeonPart) -> bool:
        '''
        Checks if a DungeonPart can be placed to the given @x, @y location
        '''
        dp_tiles = part_to_place.tiles

        for x in range(len(dp_tiles)):
            for y in range(len(dp_tiles[x])):
                # (x/y + dungeon_part.x/y) -> Relative position to World Position
                world_x = x + part_to_place.x
                world_y = y + part_to_place.y
                
                # If its a none essentail block, skip this iter
                if dp_tiles[x][y] == Tiles.IGNORE or dp_tiles[x][y] == Tiles.EMPTY_BLOCK:
                    continue
                
                # If there
                if self.tiles[world_x][world_y] != Tiles.EMPTY_BLOCK:
                    return False
        
        return True

    def update(self):
        # Create rooms in every tick
        if len(self.dungeon_parts) < self.num_rooms:
            r_width = randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
            r_height = randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)
            
            r_x = randrange(0, (self.width - r_width) - 1)
            r_y = randrange(0, (self.height - r_height) - 1)
            
            # Unused doors will be removed while creating the corridors
            r_doors = randint(MIN_ROOM_DOOR, MAX_ROOM_DOOR)

            rand_room = Room(r_x, r_y, r_height, r_width, r_doors)
            
            # Add the created room if it's placeable
            if self.canPlace(rand_room) == True:
                self.addDungenPart(rand_room)
        
def main():
    srp = SimpleRoomPlacement(5)
    srp.start()

if __name__ == "__main__":
    main()
