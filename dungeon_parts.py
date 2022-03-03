# Default Modules
import math
from typing import List
from random import randrange

from torch import le

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tile, Tiles
from utilities import Coordinate, Directions, aStar, debugTile

class DungeonPart():
    '''
    Parent dungeon part class.
    Contains the neccesary variables needed to draw the DungeonParts in 
    <dungeon_defaults.py>.RogueLikeDefaults.__drawDungeonParts()
    '''

    def __init__(self, x : int, y : int) -> None:
        '''Just crates the template variables'''

        # Location of the pivot point (upper left corner)
        # This will be used to align the parts location on the grid
        self.pivot_loc = Coordinate(x,y)

        # Tiles of the dungeon part. Mark the empty parts as Tiles.Ignore
        self.tiles : List[List[Tile]] = []
        return

    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''
        Call this after creating the dungen_parts if you want to make any changes after the main init
        Example in @Room Class with <simple_room_placement.py>
        '''
        return

class Door():
    '''A simple door object'''
    def __init__(self, x: int, y: int):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @has_corridor: True if room has a connection
        '''
        self.location = Coordinate(x,y)
        self.has_corridor = False

class Room(DungeonPart):
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''

    # Max amount of tries to place a door
    MAX_DOOR_PLACEMENT_TRIES = 5

    def __init__(self, x: int, y: int, height: int, width: int, num_doors: int, wall_color: Color = None):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @height, @width: height and width of the room in tiles
        @num_doors: number of doors for the room to have
        @wall_color: overrides the Tiles.Wall's default color.
        '''
        DungeonPart.__init__(self, x, y)
        
        # Size info
        self.height = height
        self.width = width
        
        # Room creation info
        self.num_doors = num_doors

        # Color
        self.color = wall_color

        # Create the room tiles
        # Where the corner pieces are Tiles.WALL and inner pieces are Tiles.PATH
        self.tiles = [[Tiles.WALL] * self.width for _ in range(self.height)]
        for y in range(1,self.height - 1):
            self.tiles[y][1: self.width - 1] = [Tiles.PATH] * (self.width - 2) 
        
        # Quick access for the doors.
        self.doors : List[Door] = []

        return

    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''In this case add doors to the room'''
        
        # Assign dungeon tiles
        self.dungeon_tiles = dungeon_tiles

        # Create random doors based @self.num_doors
        self.__createRandomDoors()
        # Load doors from the self.tiles
        self.__loadDoors()

    def __loadDoors(self) -> List[Door]:
        '''
        Goes through the @self.tiles and crates Door object for each of the doors.
        Appends to self.doors
        '''
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x] == Tiles.DOOR:
                    self.doors.append(Door(x,y))
        return
    

    def checkAlignedBlocks(self, location : Coordinate, tiles : List[List[Tiles]], blocks_to_check : List[Tiles], out_of_bounds_check = False):
        '''
        Checks the number of vertically and horizontally adjacent @blocks_to_check tiles around the pivot. 
        
          V = Vertical check
          |
          v
        O X O
        X P X <-- H = Horizontal Check
        O X O

        P = pivot
        X = tiles to check
        O = ignore

        @location: Location to check for aligned blocks
        @out_of_bounds_check: Also counts the areas that are out of the map as a block to check.
        @tiles: 2D matrix of tiles to check

        Returns the horizontal(x) and vertical(y) sums in Coordinate format
        '''
        vertical_sum = 0
        horizontal_sum = 0

        for i in range(-1,2):
            loc_to_check = Coordinate(location.X + i, location.Y + i)

            # Ignore the center part
            if loc_to_check.X == location.X and loc_to_check.Y == location.Y:
                continue
            
            # Check on y axis
            if loc_to_check.Y >= 0 and loc_to_check.Y < len(tiles): 
                if tiles[loc_to_check.Y][location.X] in blocks_to_check:
                    vertical_sum += 1
            elif out_of_bounds_check:
                vertical_sum += 1

            # Check on x axis
            if loc_to_check.X >= 0 and loc_to_check.X < len(tiles[0]):
                if tiles[location.Y][loc_to_check.X] in blocks_to_check:
                    horizontal_sum += 1
            elif out_of_bounds_check:
                horizontal_sum += 1
        
        return Coordinate(horizontal_sum, vertical_sum)
    
    def canPlaceDoor(self, x, y) -> bool:
        '''
        Checks if the door is placeable at the given location.
        Avoids placing doors on corner pieces, next to each other and places where the door will be blocked
        '''

        '''To wall piece to not be a corner. It should have continuing pieces either along the x or y axis
        C = piece to check
        o = empty/none blocking tile
        x = wall tile

        Not corner cases:
        case 1:          case 2:
            o x o           o o o
            o C o           x C x
            o x o           o o o

        Corner case:
        case 1:
            o x o          
            o C x         
            o o o         
        '''

        # Check if the door is being blocked by another dungeon tile and also for corner pieces
        world_aligned = self.checkAlignedBlocks(Coordinate(x + self.pivot_loc.X, y + self.pivot_loc.Y), self.dungeon_tiles, Tiles.BLOCKING_TILES, True)
        world_check = (world_aligned.X == 2 and world_aligned.Y == 0) or (world_aligned.Y == 2 and world_aligned.X == 0)
        
        # Check if the door is next to another door
        door_aligned = self.checkAlignedBlocks(Coordinate(x, y), self.tiles, [Tiles.DOOR], False)
        door_check = door_aligned.X + door_aligned.Y == 0

        return world_check and door_check

    def __createRandomDoors(self):
        '''
        Creates doors on random locations around the walls based on the @self.num_rooms
        '''
        # Number of tries
        tries = 0

        # Get all the wall locations and index them by adding them to an array
        wall_locations : List[Coordinate] = []
        
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x] == Tiles.WALL:
                    wall_locations.append(Coordinate(x,y))

        # Select random door locations
        while(len(self.doors) < self.num_doors) and tries < self.MAX_DOOR_PLACEMENT_TRIES:
            random_loc = randrange(0, len(wall_locations))
            check_loc = wall_locations[random_loc]
  
            # Don't add door if the door is not placable or a door is already added to that location
            if (self.canPlaceDoor(check_loc.X,check_loc.Y) == False or self.tiles[check_loc.Y][check_loc.X] == Tiles.DOOR):
                tries += 1
                continue
            
            # Add door
            self.doors.append(Door(check_loc.X,check_loc.Y))
            self.tiles[check_loc.Y][check_loc.X] = Tiles.DOOR

            # Reset the number of tries
            tries = 0
        
        return

class CustomRoom(Room):
    '''
    A room where you create your custom room by giving the room scheme as input
    '''

    def __init__(self, x: int, y: int, room_layout : str):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @room_layout: room's layout in string. 
        See the example in the <dungeon_parts.py>.CustomRoom or README.md
        '''
        
        '''
        x = wall
        o = walkable area
        D = Door
        '''
        example_room_layout = '''\
        x x x x
        x o o x
        x o o D
        x x x x
        '''
        DungeonPart.__init__(self, x, y)

        # Seperates the string into 2d array and crates a new array based on the values 
        self.tiles = [[self.__layoutToTile(i) for i in line.split()] for line in room_layout.splitlines()]
        
        # Quick access for the doors.
        self.doors = []
        # Load doors from the self.tiles
        self.__loadDoors()

        return

    def __layoutToTile(self, layout_str : str):
        '''
        Converts the string layout elements to Tiles
        x = wall
        o = walkable area
        D = Door
        '''
        if layout_str == "x":
            return Tiles.WALL
        elif layout_str == "o":
            return Tiles.PATH
        elif layout_str == "D":
            return Tiles.DOOR
        else:
            return Tiles.IGNORE

class Corridor(DungeonPart):
    '''
    Base class to create corridors from the given @start_pos to @end_pos by using the A* pathfinding algorithm.
    Only consists the basic variables. Not functional. Use the other variations instead
    '''
    def __init__(self, start : Coordinate, end : Coordinate, color: Color = None):
        '''
        @start_x, @start_y: starting position of the corridor
        @end_x, @end_y: final position of the corridor
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        DungeonPart.__init__(self, 0, 0)

        # Location info
        # Start position
        self.start = start

        # End position
        self.end = end

        # Tiles
        self.tiles = []

    
    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''In this case add doors to the room'''
        
        # Assign dungeon tiles
        self.dungeon_tiles = dungeon_tiles

        # Adjust tiles size
        self.tiles = [[Tiles.IGNORE] * len(self.dungeon_tiles[0]) for _ in range(len(self.dungeon_tiles))]

        # Create the corridor
        self.createCorridor()


    def createCorridor(self):
        '''
        Gets called during __init__
        Extend this create the corridor by filling its shape in @self.tiles
        '''

        #debugTile(self.dungeon_tiles,multiple_points=[self.start,self.end])

        # print("Applying algorithm")
        # Get the corridor path
        corridor_path = aStar(self.start, self.end, [], self.dungeon_tiles, [Tiles.EMPTY_BLOCK, Tiles.DOOR])
        # print("Applyed algorithm")

        # Convert the path to tiles and get the furthest points of the path to be used later
        left_corner = None
        right_corner = None

        for coord in corridor_path:
            self.tiles[coord.Y][coord.X] = Tiles.PATH

            # Get the top left and bottom right corners of the area that contains the corridor
            if left_corner == None and right_corner == None:
                left_corner = coord
                right_corner = coord
            
            if coord.X < left_corner.X:
                left_corner.X = coord.X
            if coord.Y < left_corner.Y:
                left_corner.Y = coord.Y   

            if coord.X > right_corner.X:
                right_corner.X = coord.X
            if coord.Y > right_corner.Y:
                right_corner.Y = coord.Y   

 
        # Adjust tile dimensions to fit the corridor precisly
        # debugTile(self.tiles,multiple_points=corridor_path)
        # self.tiles = [self.tiles[i][left_corner.X:right_corner.X + 1] for i in range(left_corner.Y,right_corner.Y + 1)]
        # debugTile(self.tiles)

    def fitFromDirection(self, direction : Coordinate):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                pass
        

