# Custom Modules
from color_constants import Color

# If further settings are needed
class Tile():  
    
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