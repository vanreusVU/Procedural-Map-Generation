# Default Modules
from turtle import width
from typing import List
from random import randint

# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles
from dungeon_parts import CustomRoom, DungeonPart, Room
from utilities import aStar, Coordinate, MinMax, debugTile

# Max number of tries to place a room
MAX_PLACEMANT_TRIES = 500

NUM_ROOMS = MinMax(3,5)
ROOM_WIDTH = MinMax(3,5)
ROOM_HEIGHT = MinMax(3,5)
ROOM_DOOR = MinMax(1,2)

HEIGHT = 15
WIDTH = 15
GRID_SIZE = 50
FPS = 10

class SimpleRoomPlacement(RogueLikeDefaults):
    '''Simple Room Placement Algorithm for random dungeon generation'''
    
    def __init__(self, num_rooms: int = 0, custom_rooms: List[CustomRoom] = []):
        '''
        @num_rooms: number of randomly generated rooms to create and place on the map.
        if set, will ignore @custom_rooms
        @custom_rooms: custom rooms to place on the map
        
        '''

        RogueLikeDefaults.__init__(self,
            height=HEIGHT,
            width=WIDTH,
            grid_size=GRID_SIZE,
            fps=FPS)

        # Setting up room settings
        self.num_rooms = randint(NUM_ROOMS.MIN, NUM_ROOMS.MAX)
        self.custom_rooms = custom_rooms
        

    def createRooms(self):
        ''' Create rooms '''
        # Number of tries
        tries = 0

        # Place rooms until enough rooms have been placed.
        # Will try to place a room @MAX_PLACEMANT_TRIES times and if it's still not a sucess it will 
        # stop placing rooms. The @tries gets reseted after every successfull placement.
        while len(self.dungeon_parts) < self.num_rooms and tries < MAX_PLACEMANT_TRIES:
            r_width = randint(ROOM_WIDTH.MIN, ROOM_WIDTH.MAX)
            r_height = randint(ROOM_HEIGHT.MIN, ROOM_HEIGHT.MAX)
            
            r_x = randint(0, (self.width - r_width))
            r_y = randint(0, (self.height - r_height))
            
            # Unused doors will be removed while creating the corridors
            r_doors = randint(ROOM_DOOR.MIN, ROOM_DOOR.MAX)

            rand_room = Room(r_x, r_y, r_height, r_width, r_doors, self.dungeon_tiles)
            
            # Increase the number of tries
            tries += 1

            # Add the created room if it's placeable
            if self.canPlace(rand_room) == True:
                self.addDungenPart(rand_room)

                # Reset the number of tries
                tries = 0

        # Update the tiles
        for part in self.dungeon_parts:
            print("Adding doors")
            part.afterInit(self.dungeon_tiles)

        # TODO: A* Debug. Remove LATER
        shorthest_path = aStar(Coordinate(0,0),Coordinate(WIDTH - 1, HEIGHT - 1),[],self.dungeon_tiles,[Tiles.EMPTY_BLOCK,Tiles.WALL,Tiles.PATH])
        debugTile(self.dungeon_tiles,multiple_points=shorthest_path)

    def canPlace(self, part_to_place: DungeonPart) -> bool:
        '''
        Checks if a DungeonPart can be placed to the given @x, @y location
        '''
        dp_tiles = part_to_place.tiles

        for y in range(len(dp_tiles)):
            for x in range(len(dp_tiles[y])):
                # (x/y + dungeon_part.x/y) -> Relative position to World Position
                world_x = x + part_to_place.pivot_loc.X
                world_y = y + part_to_place.pivot_loc.Y
                
                # If its a none essentail block, skip this iter
                if dp_tiles[y][x] == Tiles.IGNORE or dp_tiles[y][x] == Tiles.EMPTY_BLOCK:
                    continue
                
                # If there
                if self.dungeon_tiles[world_y][world_x] != Tiles.EMPTY_BLOCK:
                    return False
        
        return True

    def begin(self):
        # Create the rooms
        self.createRooms() 
        return

    def update(self):
        return
        
def main():
    srp = SimpleRoomPlacement(NUM_ROOMS)
    srp.start()

if __name__ == "__main__":
    main()
