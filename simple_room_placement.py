# Default Modules
from typing import List
from random import randint, randrange
import time

# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles
from dungeon_parts import CustomRoom, DungeonPart, Room, Corridor, Door
from utilities import Coordinate, MinMax
from path_finding import distancePythagorean
from triangulation import delaunayTriangulation

# Max number of tries to place a room
MAX_PLACEMANT_TRIES = 500

NUM_ROOMS = MinMax(10,15)
ROOM_WIDTH = MinMax(4,10)
ROOM_HEIGHT = MinMax(4,10)
ROOM_DOOR = MinMax(1,2)

HEIGHT = 80
WIDTH = 80
GRID_SIZE = 15
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
        self.triangulation = []
        

    def createRooms(self):
        ''' Create rooms '''
        # Number of tries
        tries = 0
        rooms_created = 0

        # Place rooms until enough rooms have been placed.
        # Will try to place a room @MAX_PLACEMANT_TRIES times and if it's still not a sucess it will 
        # stop placing rooms. The @tries gets reseted after every successfull placement.
        while rooms_created < self.num_rooms and tries < MAX_PLACEMANT_TRIES:
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
                rooms_created += 1

                # Reset the number of tries
                tries = 0

        # Update the rooms
        for part in self.dungeon_parts:
            if isinstance(part,Room):
                part.afterInit(self.dungeon_tiles)

    def findRoomConnections(self):
        ''' Decide on the routes to be connected '''
        
        room_coordinates : List[Coordinate] = [Coordinate(part.pivot_loc.X * GRID_SIZE, part.pivot_loc.Y * GRID_SIZE) for part in self.dungeon_parts if isinstance(part, Room)]
        self.triangulation = delaunayTriangulation(room_coordinates)

        visited : List[Coordinate] = room_coordinates[0]

    def drawRoomConnections(self):
        ''' Draw room connections '''

        for triangle in self.triangulation:
            for edge in triangle.edges:
                pygame.draw.line(self.SCREEN, Color.RED, edge.p1.getTuple(), edge.p2.getTuple(), 3)
            pygame.draw.circle(self.SCREEN , Color.WHITE, triangle.pivot_vertex.getTuple(), 5)
 
    def createCorridors(self):
        ''' Creates corridors '''

        # Number of tries
        tries = 0
        corridors_created = 0

        # Place corridors until all the doors have a connection.
        # Will try to place a corridor @MAX_PLACEMANT_TRIES times and if it's still not a sucess it will 
        # stop placing corridors. The @tries gets reseted after every successfull placement.
        for part in self.dungeon_parts:
            if isinstance(part,Room):
                room : Room = part
                door_to_connect = self.getRandomDoor(room)

                closest_room = self.getClosestRoom(room)
                door_to_be_connected = self.getRandomDoor(closest_room)

                if door_to_connect != None and door_to_be_connected != None:
                    corridor = Corridor(door_to_connect.location + room.pivot_loc,door_to_be_connected.location + closest_room.pivot_loc)
                    door_to_connect.has_corridor = True
                    door_to_be_connected.has_corridor = True

                    self.addDungenPart(corridor)
                    corridors_created += 1

                    

        # Update the rooms
        for part in self.dungeon_parts:
            if isinstance(part,Corridor):
                part.afterInit(self.dungeon_tiles)
        
        pass

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

    def getClosestRoom(self, room_to_check : Room) -> Room:
        '''
        Returns the closest room to the given room
        '''
        closest_room : Room = None
        closest_room_distance = 0

        if room_to_check == None:
            return None

        for part in self.dungeon_parts:
            if isinstance(part,Room) and part != room_to_check:
                distance = distancePythagorean(room_to_check.pivot_loc, part.pivot_loc)
                
                if closest_room == None:
                    closest_room = part
                    closest_room_distance = distance
                    continue

                if distance < closest_room_distance:
                    closest_room = part
                    closest_room_distance = distance
        
        return closest_room

    def getRandomDoor(self, room_to_check : Room, allow_multiple_connection : bool = False) -> Door:
        '''
        Returns a random door from the given room    
        '''

        if allow_multiple_connection:
            available_doors = room_to_check.doors
        else:
            available_doors = [a for a in room_to_check.doors if a.has_corridor == False]
        
        if len(available_doors) > 0:
            door_to_pick = randrange(0,len(available_doors))
            return available_doors[door_to_pick]
        
        return None
        

    def begin(self):
        # Create the rooms
        self.createRooms() 
        
        # Make connections
        self.findRoomConnections()

        # Draw room connections
        self.drawRoomConnections()

        # Create the corridors
        #self.createCorridors()
        return

    def update(self):
        return
        
def main():
    srp = SimpleRoomPlacement(NUM_ROOMS)
    srp.start()

if __name__ == "__main__":
    main()
