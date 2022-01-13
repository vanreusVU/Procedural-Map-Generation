# Custom Modules
from re import S
from tracemalloc import start
from typing import Tuple
from color_constants import Color
from utilities import Coordinate

# If further settings are needed
class Tile():  
    '''Tile object to be used to define different types of tiles'''
    def __init__(self, size_ratio : int, color : Color):
        '''
        @size_ratio: if 100 the tile will fill the grid, 
        50 means the tile's size will be half of the grid size.
        Size of the tile compared to the grid size in %.
        
        @color: color of the block
        '''
        self.size_ratio = max(min(size_ratio, 100), 1) # Clamp to value between 1 and 100 
        self.color = color

class Tiles():
    ''' 
    Tile constants to be used in creating the dungeon.
    Each constants is derived from @Tile class
    '''
    EMPTY_BLOCK = Tile(20, Color.WHITE)
    WALL = Tile(100, Color.BROWN)
    PATH = Tile(80, Color.RED)

class Room():
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''
    def __init__(self, x: int, y: int, height: int, width: int, color: Color = None):
        '''
        @x, @y: location of the pivot (top left corner) of the room
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        # Location info
        self.x = x
        self.y = y
        
        # Size info
        self.height = height
        self.width = width
        
        # Create the tiles
        self.tiles = [[Tiles.WALL] * width for _ in range(height)]
        return

class Corridor():
    '''
    Creates a corridor from the given @start_pos to @end_pos, @color.
    '''
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y:int, color: Color = None):
        '''
        @start_x, @start_y: starting position of the 
        @height, @width: height and width of the room in tiles
        @color: overrides the Tiles default color.
        '''
        # Location info
        # Start position
        self.start_x = start_x
        self.start_y = start_y

        # End position
        self.end_x = end_x
        self.end_y = end_y
        
        # Create the tiles
        self.tiles = [[Tiles.WALL] * width for _ in range(height)]
        return