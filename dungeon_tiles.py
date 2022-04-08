# Custom Modules
from color_constants import Color

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
    EMPTY_BLOCK = Tile(5, Color.WHITE) # Means its a out of map empty block
    WALL = Tile(100, Color.RED) # Wall/Room
    PATH = Tile(90, Color.WHITE) # Path/Corridor
    DOOR = Tile(80, Color.BROWN) # Door
    IGNORE = None # Means ignore this tile while drawing and keep whatever is already there

    SOFT_IGNORE_WALL = Tile(100, Color.RED) # DON'T USE THIS. ITS USED FOR A* PATHFINDING

    # Tile groups
    BLOCKING_TILES = [WALL, DOOR]
    SAFE_TILES = [IGNORE, EMPTY_BLOCK, PATH]