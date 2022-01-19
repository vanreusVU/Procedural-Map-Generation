# Default Modules
from turtle import width
from typing import List
from random import randrange

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tile, Tiles

class DungeonPart():
    '''
    Parent dungeon part class.
    Contains the neccesary variables needed to draw the DungeonParts in 
    <dungeon_defaults.py>.RogueLikeDefaults.__drawDungeonParts()
    '''

    def __init__(self) -> None:
        '''Just crates the template variables'''

        # Location of the pivot point (upper left corner)
        # This will be used to align the parts location on the grid
        self.x : int = 0
        self.y : int = 0

        # Tiles of the dungeon part. Mark the empty parts as Tiles.Ignore
        self.tiles : List[List[Tile]] = []
        return

class Door():
    '''A simple door object'''
    def __init__(self, x: int, y: int):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @has_corridor: True if room has a connection
        '''
        self.x = x
        self.y = y
        self.has_corridor = False

class Room(DungeonPart):
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''
    def __init__(self, x: int, y: int, height: int, width: int, num_doors: int, wall_color: Color = None):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @height, @width: height and width of the room in tiles
        @num_doors: number of doors for the room to have
        @wall_color: overrides the Tiles.Wall's default color.
        '''
        DungeonPart.__init__(self)

        # Location info
        self.x = x
        self.y = y
        
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
        for x in range(1,self.height - 1):
            self.tiles[x][1: self.width - 1] = [Tiles.PATH] * (self.width - 2) 
        
        # Create random doors based @self.num_doors
        self.__createRandomDoors()
        # Quick access for the doors.
        self.doors = []
        # Load doors from the self.tiles
        self.__loadDoors()

        return

    def __loadDoors(self) -> List[Door]:
        '''
        Goes through the @self.tiles and crates Door object for each of the doors.
        Appends to self.doors
        '''
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                if self.tiles[x][y] == Tiles.DOOR:
                    self.doors.append(Door(x,y))
        return
    
    def __isCornerWallPiece(self, x, y):
        '''
        Check if the Tiles.Wall is a corner piece. To avoid placing doors on corner pieces and next to each other
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
        '''
        vertical_sum = 0
        horizontal_sum = 0

        # Could be done way simpler, but wanted to do it this way for the fun of it
        for i in range(-1,2):
            check_x = x + i
            check_y = y + i
            
            # Weather the piece to be check is out of the bounds
            if check_x >= 0 and check_x < self.width:
                if self.tiles[x][check_y] == Tiles.WALL:
                    vertical_sum += 1
            
            if check_y >= 0 and check_y < self.height:
                if self.tiles[check_x][y] == Tiles.WALL:
                    horizontal_sum += 1

        if (vertical_sum == 3 and horizontal_sum <= 1) or (vertical_sum <= 1 and horizontal_sum == 3):
            return False

        return True 

    def __createRandomDoors(self):
        '''
        Creates doors on random locations around the walls based on the @self.num_rooms
        '''
        room_locs = []
        
        # Calculate the perimeter (-2) is for shared pieces
        num_walls = (self.height * 2) + ((self.width - 2) * 2)

        # TODO: if random_loc is not a corner piece create a different random loc

        # Select random door locations
        while(len(room_locs) < self.num_doors):
            random_loc = randrange(0, num_walls)
            
            # Make sure that the random_loc doesn't already exists
            if random_loc in room_locs:
                continue

            room_locs.append(random_loc)
        
        # Set the tiles
        wall_counter = 0
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                if self.tiles[x][y] == Tiles.WALL:
                    if wall_counter in room_locs:
                        self.tiles[x][y] = Tiles.DOOR

                    wall_counter += 1
                    
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
    Base class to create corridors from the given @start_pos to @end_pos, @color.
    Only consists the basic variables. Not functional. Use the other variations instead
    '''
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y:int, color: Color = None):
        '''
        @start_x, @start_y: starting position of the corridor
        @end_x, @end_y: final position of the corridor
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        DungeonPart.__init__(self)

        # Location info
        # Start position
        self.start_x = start_x
        self.start_y = start_y

        # End position
        self.end_x = end_x
        self.end_y = end_y

        self.width = abs(start_x - end_x)
        self.height = abs(start_y - end_y)

        # Tiles
        self.tiles = [[Tiles.IGNORE] * self.width for _ in range(self.height)]
        
        self.createCorridor()

    def createCorridor(self):
        '''
        Gets called during __init__
        Extend this create the corridor by filling its shape in @self.tiles
        '''
        return None

class AS_Corridor(Corridor):
    '''
    AS Corridor: Crates a corridor from the given @start_pos to @end_pos by using the A* pathfinding algorithm.
    Only consists the basic variables. Not functional. Use the other variations instead
    '''

    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int, dungeon_parts : List[DungeonPart], color: Color = None):
        '''
        @start_x, @start_y: relative starting position of the corridor
        @end_x, @end_y: final position of the corridor
        @height, @width: height and width of the room in tiles
        @dungeon_parts: Current dungeon parts on the level.
        By default use this -> <dungeon_defaults.py>.RogueLikeDefaults.dungeon_parts
        @color: overrides the Tiles default color.
        '''
        Corridor.__init__(start_x, start_y, end_x, end_y, color)

    def createCorridor(self):
        '''More info on A*: https://en.wikipedia.org/wiki/A*_search_algorithm'''
