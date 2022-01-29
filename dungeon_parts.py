# Default Modules
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

    def __init__(self, x : int, y : int, dungeon_tiles : List[List[Tiles]]) -> None:
        '''Just crates the template variables'''

        # Location of the pivot point (upper left corner)
        # This will be used to align the parts location on the grid
        self.x : int = x
        self.y : int = y

        # Current dungeon tiles
        self.dungeon_tiles = dungeon_tiles

        # Tiles of the dungeon part. Mark the empty parts as Tiles.Ignore
        self.tiles : List[List[Tile]] = []
        return

    def afterInit(self):
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
        self.x = x
        self.y = y
        self.has_corridor = False

class Room(DungeonPart):
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''
    def __init__(self, x: int, y: int, height: int, width: int, num_doors: int, dungeon_tiles : List[List[Tiles]], wall_color: Color = None):
        '''
        @x, @y: relative location of the pivot (top left corner) of the room
        @height, @width: height and width of the room in tiles
        @num_doors: number of doors for the room to have
        @wall_color: overrides the Tiles.Wall's default color.
        '''
        DungeonPart.__init__(self, x, y, dungeon_tiles)
        
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
        
        # Quick access for the doors.
        self.doors : List[Door] = []

        return

    def afterInit(self):
        '''In this case add doors to the room'''

        # Create random doors based @self.num_doors
        self.__createRandomDoors()
        # Load doors from the self.tiles
        self.__loadDoors()

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
    

    def checkAlignedBlocks(self, x, y, tiles):
        '''
        Checks the number of vertically and horizontally adjacent blocking tiles around the pivot
        
          V = Vertical check
        O X O
        X P X H = Horizontal Check
        O X O

        P = pivot
        X = tiles to check
        O = ignore

        @x, @y: Location to check for aligned blocks
        @tiles: 2D matrix to check

        Returns a tuple of verticall and horizontal sums
        [0] = Number of blocking tiles horizontally
        [1] = Number of blocking tiles vertically
        '''

        vertical_sum = 0
        horizontal_sum = 0
        
        for i in range(-1,2):
            check_x = x + i
            check_y = y + i

            # Ignore the center part
            if i == 0:
                continue

            if check_y >= 0 and check_y < len(tiles[0]): 
                if tiles[x][check_y] in Tiles.BLOCKING_TILES:
                    vertical_sum += 1

            if check_x >= 0 and check_x < len(tiles):
                if tiles[check_x][y] in Tiles.BLOCKING_TILES:
                    horizontal_sum += 1

        # print(horizontal_sum, vertical_sum)
        return (horizontal_sum, vertical_sum)
    
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

        # Check for corner pieces and placing next to another door
        local_check = self.checkAlignedBlocks(x,y,self.tiles)

        if (local_check[0] >= 1 and local_check[1] == 0) or (local_check[1] >= 1 and local_check[0] == 0):
            return False

        # Check if the door is being blocked by another dungeon tile
        world_check = self.checkAlignedBlocks(x + self.x, y + self.y,self.dungeon_tiles)

        if (world_check[0] >= 1 and world_check[1] == 0) or (world_check[1] >= 1 and world_check[0] == 0):
            return False

        ''' print("LC_H:",local_check[0],"LC_V",local_check[1])
        print("WC_H:",world_check[0],"WC_V",world_check[1])'''
        return True

    def __createRandomDoors(self):
        '''
        Creates doors on random locations around the walls based on the @self.num_rooms
        '''
        room_locs = []

        # Get all the wall locations and index them by adding them to an array
        # Tuple (x,y) for wall locations
        wall_locations = []
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                if self.tiles[x][y] == Tiles.WALL:
                    wall_locations.append((x,y))

        # Select random door locations
        while(len(self.doors) < self.num_doors):
            random_loc = randrange(0, len(wall_locations))
            selected_location = wall_locations[random_loc]
            
            # Could be changed with a coordinate class
            x = selected_location[0]
            y = selected_location[1]

            # If its already a door, corner wall piece or next to an another door then find another location
            if self.canPlaceDoor(x,y) == True or self.tiles[x][y] != Tiles.WALL:
                continue

            self.doors.append(Door(x,y))
            self.tiles[x][y] = Tiles.DOOR
        
        return

class CustomRoom(Room):
    '''
    A room where you create your custom room by giving the room scheme as input
    '''

    def __init__(self, x: int, y: int, room_layout : str, dungeon_tiles : List[List[Tiles]]):
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
        DungeonPart.__init__(self, x, y, dungeon_tiles)

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
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y:int, dungeon_tiles : List[List[Tiles]], color: Color = None):
        '''
        @start_x, @start_y: starting position of the corridor
        @end_x, @end_y: final position of the corridor
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        DungeonPart.__init__(self, -1, -1, dungeon_tiles)

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

    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int,  dungeon_tiles : List[List[Tiles]], color: Color = None):
        '''
        @start_x, @start_y: relative starting position of the corridor
        @end_x, @end_y: final position of the corridor
        @height, @width: height and width of the room in tiles
        @dungeon_parts: Current dungeon parts on the level.
        By default use this -> <dungeon_defaults.py>.RogueLikeDefaults.dungeon_parts
        @color: overrides the Tiles default color.
        '''
        Corridor.__init__(start_x, start_y, end_x, end_y, dungeon_tiles, color)

    def createCorridor(self):
        '''More info on A*: https://en.wikipedia.org/wiki/A*_search_algorithm'''
