# Default Modules
from enum import Enum
from typing import List

# Custom Modules
from dungeon_tiles import Tiles

class Coordinate():
    ''' Simple Coordinate class'''

    def __init__(self, x: int, y: int) -> None:
        '''Defines x and y variables'''
        self.X = x
        self.Y = y
        pass

    def __str__(self) -> str:
        return f"X: {self.X}, Y: {self.Y}"

    def __add__(self, add_me):
        x = self.X + add_me.X
        y = self.Y + add_me.Y
        return Coordinate(x,y)

class MinMax():
    ''' Simple MinMax class'''

    def __init__(self, min: int, max: int) -> None:
        '''Defines x and y variables'''
        self.MIN = min
        self.MAX = max
        pass

    def __str__(self) -> str:
        return f"MIN: {self.MIN}, MAX: {self.MAX}"

class Directions(Enum):
    ''' Simple Direction class consisting of 4 dicrectional coordinate constants'''
    
    NORTH = Coordinate(0,-1)
    EAST = Coordinate(1,0)
    SOUTH = Coordinate(0,1)
    WEST = Coordinate(-1,0)

def isWithinBounds(location : Coordinate, tiles : List[List[Tiles]]) -> bool:
    '''
    Checks if the given location is within the bounds of the tiles
    '''
    
    return (location.Y >= 0 and location.Y < len(tiles)) and (location.X >= 0 and location.X < len(tiles[0]))

def debugTile(tiles : List[List[Tiles]], single_point : Coordinate = Coordinate(-1,-1), single_point_mark : str = "▣", multiple_points : List[Coordinate] = [], multiple_points_mark : str = "▣"):
    '''
        Prints out the tiles 
    '''

    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            if single_point.X == x and single_point.Y == y:
                print(single_point_mark, end=" ")
            elif True in [True if a.X == x and a.Y == y else False for a in multiple_points]:
                print(multiple_points_mark, end=" ")
            elif tiles[y][x] in Tiles.BLOCKING_TILES:
                print("■", end=" ")
            else:
                print("◻", end=" ")
            
        print()
    
    print()