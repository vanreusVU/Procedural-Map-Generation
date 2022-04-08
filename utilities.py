# Default Modules
from enum import Enum
from typing import List, Tuple
import random

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

def getPercentage(number, percentage) -> float:
        '''returns the x% of the number

        :param number: number to take the percentage of
        :type number: any numeric type
        :param percentage: percentage to be taken (0-100)
        :type percentage: any numeric type
        :return: floored percentage
        :rtype: float
        '''        
        return (number/100)*percentage

def percentageDifference(number1, number2):
    '''
    Percentage difference between number1 and number2
    - means number2 is that percent less than number1

    :param number1: number1 to compare
    :type number1: any numeric type
    :param number2: number to be compared
    :type number2: any numeric type
    :return: percentage difference between number1 and number2
    :rtype: float
    '''    

    # If one of the numbers is 0 then we need to increase both of the numbers so that the
    # difference is the same but no 0 exists. !!Division by 0 is not possible!!
    while number1 == 0 or number2 == 0:
        number1 += 1
        number2 += 1

    return ((number2 - number1) / (number1)) * 100

class SquareArea():
    ''' Basic tree node '''
    def __init__(self, location : Coordinate, width : int, height : int) -> None:
        self.location = location
        self.width = width 
        self.height = height
        self.child_squares : List[SquareArea] = []

    def splitHorizontally(self, shift_percentage : int = 0):
        ''' Split the owning squarearea horizontally
        
        :param shift_percentage: max amount that the mid-line can move towards one of the sides, defaults to 10
        :type shift_percentage: int, optional
        :return: Resulting parts
        :rtype: [SquareArea, SquareArea]
        '''    

        # Mid line
        mid_line = int(self.width / 2)

        # Shift amount
        max_shift_amount = int(getPercentage(mid_line, shift_percentage))

        # The result will be the mid point where we will split the areas
        split_loc_x = mid_line + random.randint(-max_shift_amount, max_shift_amount)

        # Part before the splitting line
        area1 : SquareArea = SquareArea(self.location, split_loc_x, self.height)
        
        # Part after the splitting line
        area2_location : Coordinate = Coordinate((self.location.X + split_loc_x), self.location.Y)
        area2 : SquareArea = SquareArea(area2_location, self.width - split_loc_x, self.height)

        return [area1, area2]

    def splitVertically(self, shift_percentage : int = 0):
        ''' Split the owning squarearea vertically

        :param shift_percentage: max amount that the mid-line can move towards either sides, defaults to 0
        :type shift_percentage: int, optional
        :return: Resulting parts
        :rtype: [SquareArea, SquareArea]
        '''        

        # Mid line
        mid_line = int(self.height / 2)

        # Shift amount
        max_shift_amount = int(getPercentage(mid_line, shift_percentage))

        # The result will be the mid point where we will split the areas
        split_loc_y = mid_line + random.randint(-max_shift_amount, max_shift_amount)

        # Part before the splitting line
        area1 : SquareArea = SquareArea(self.location, self.width, split_loc_y)
        
        # Part after the splitting line
        area2_location : Coordinate = Coordinate(self.location.X, self.location.Y + split_loc_y)
        area2 : SquareArea = SquareArea(area2_location, self.width, self.height - split_loc_y)

        return [area1, area2]


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
            elif tiles[y][x] == Tiles.PATH:
                print("⧯", end=" ")
            else:
                print("◻", end=" ")
            
        print()
    print()

def checkAlignedBlocks( location : Coordinate, tiles : List[List[Tiles]], blocks_to_check : List[Tiles], out_of_bounds_check = False) -> Coordinate:
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

    :param location: Location to check for aligned blocks
    :type location: Coordinate
    :param tiles: 2D matrix of tiles to check
    :type tiles: List[List[Tiles]]
    :param blocks_to_check: blocks to check around the location
    :type blocks_to_check: List[Tiles]
    :param out_of_bounds_check: counts the areas that are out of the map as a block to check., defaults to False
    :type out_of_bounds_check: bool, optional
    :return:  Returns the horizontal(x) and vertical(y) sums in Coordinate format
    :rtype: Coordinate
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

def globalToRelative(point_of_origin: Coordinate, global_point: Coordinate) -> Coordinate:
    ''' Turns global location into relative

    :param point_of_origin: Pivot point of the relative location
    :type point_of_origin: Coordinate
    :param global_point: Global location to be turned into relative
    :type global_point: Coordinate
    :return: new relative location
    :rtype: Coordinate
    '''    

    relative_coord : Coordinate = global_point - point_of_origin
    
    if relative_coord.X < 0 or relative_coord.Y < 0:
        # print("WARNING: Relative point is behind the origin point")
        return Coordinate(-1, -1)

    return relative_coord