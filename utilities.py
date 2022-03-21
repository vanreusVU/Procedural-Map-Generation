# Default Modules
from enum import Enum
from typing import List, Tuple

# Custom Modules
from dungeon_tiles import Tiles

class Coordinate():
    ''' Simple Coordinate class'''

    def __init__(self, x: int, y: int) -> None:
        '''Defines x and y variables'''
        self.X = x
        self.Y = y
        pass

    def getTuple(self) -> Tuple[int, int]:
        '''
        Transforms Coordinate into a tupe of x: [0] y: [1]

        :return: coordinate in tuple format
        :rtype: Tuple[int, int]
        '''        
        return (self.X, self.Y)     

    def __str__(self) -> str:
        return f"X: {self.X}, Y: {self.Y}"

    def __add__(self, __o : object):
        ''' Override Coordinate addition. Adds the x and y positions of both objects and returns the result coordinate'''
        x = self.X + __o.X
        y = self.Y + __o.Y
        return Coordinate(x,y)

    def __sub__(self, __o : object):
        ''' Override Coordinate subtraction. Subtracts the x and y positions of both objects and returns the result coordinate'''
        x = self.X - __o.X
        y = self.Y - __o.Y
        return Coordinate(x,y)

    def __eq__(self, __o: object) -> bool:
        ''' 
        Equality checks are based on the X and Y values rather than instances 
        !if the compared object is member of the same class
        '''

        if isinstance(__o, Coordinate) or isinstance(__o, list):
            if isinstance(__o, list):
                __o = __o[0]
            return __o.X == self.X and __o.Y == self.Y
        else:
            return super(Coordinate, self).__eq__(__o)

    def __ne__(self, __o: object) -> bool:
        ''' 
        Not-Equality checks are based on the X and Y values rather than instances 
        !if the compared object is member of the same class
        '''
        
        if isinstance(__o, Coordinate):
            if isinstance(__o, list):
                __o = __o[0]
            return __o.X != self.X or __o.Y != self.Y
        else:
            return super(Coordinate, self).__ne__(__o)

class BasicNode():
    ''' Basic tree node '''
    def __init__(self, data) -> None:
        self.data = data
        self.connected_nodes : List[BasicNode] = []

class MinMax():
    ''' Simple class that holds two variables under the name of MIN and MAX.'''

    def __init__(self, min, max) -> None:
        '''Defines min and max variables'''
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

    :param location: location to check
    :type location: Coordinate
    :param tiles: 2D matrix to check the bounds for 
    :type tiles: List[List[Tiles]]
    :return: weather the location is within the bounds of the matrix
    :retval True: location within bounds
    :retval False: location is out of bounds
    :rtype: bool
    '''    
    
    return (location.Y >= 0 and location.Y < len(tiles)) and (location.X >= 0 and location.X < len(tiles[0]))  

# TODO: Debug function remove later
def debugTile(tiles : List[List[Tiles]], single_point : Coordinate = Coordinate(-1,-1), single_point_mark : str = "▣", multiple_points : List[Coordinate] = [], multiple_points_mark : str = "▣"):

    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            if single_point.X == x and single_point.Y == y:
                print(single_point_mark, end=" ")
            elif True in [True if a.X == x and a.Y == y else False for a in multiple_points]:
                print(multiple_points_mark, end=" ")
            elif tiles[y][x] == Tiles.DOOR:
                print("⚿", end = " ")
            elif tiles[y][x] in Tiles.BLOCKING_TILES:
                print("■", end=" ")
            else:
                print("◻", end=" ")
            
        print()
    print()
