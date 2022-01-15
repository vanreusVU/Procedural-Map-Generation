# Custom Modules
from typing import List
from color_constants import Color
from dungeon_tiles import Tile, Tiles

class DungeonPart():
    '''
    Parent dungeon part class.
    Contains the neccesary variables needed to draw the DungeonParts in 
    <dungeon_defaults.py> -> RogueLikeDefaults.__drawDungeonParts()
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

class Room(DungeonPart):
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''
    def __init__(self, x: int, y: int, height: int, width: int, wall_color: Color = None):
        '''
        @x, @y: location of the pivot (top left corner) of the room
        @height, @width: height and width of the room in tiles
        @wall_color: overrides the Tiles.Wall's default color.
        '''
        DungeonPart.__init__(self)

        # Location info
        self.x = x
        self.y = y
        
        # Size info
        self.height = height
        self.width = width
        
        # Create the room tiles
        # Where the corner pieces are Tiles.WALL and inner pieces are Tiles.PATH
        self.tiles = [[Tiles.WALL] * self.width for _ in range(self.height)]
        for x in range(1,self.height - 1):
            self.tiles[x][1: self.width - 1] = [Tiles.PATH] * (self.width - 2) 
        
        return

class CustomRoom(Room):
    '''
    A room where you create your custom room by giving the room scheme as input
    '''

    def __init__(self, x: int, y: int, room_layout : str):
        '''
        @x, @y: location of the pivot (top left corner) of the room
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
        
        room_layout = [[i for i in line.split()] for line in room_layout.splitlines()]
        
        pass

        

class Corridor(DungeonPart):
    '''
    Base class to create corridors from the given @start_pos to @end_pos, @color.
    Only consists the basic variables. Not functional. Use the other variations instead
    '''
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y:int, color: Color = None):
        '''
        @start_x, @start_y: starting position of the 
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

    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int, dungeon_parts : List[List[DungeonPart]], color: Color = None):
        '''
        @start_x, @start_y: starting position of the 
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        Corridor.__init__(start_x, start_y, end_x, end_y, color)

    def createCorridor(self):
        '''More info on A*: https://en.wikipedia.org/wiki/A*_search_algorithm'''










