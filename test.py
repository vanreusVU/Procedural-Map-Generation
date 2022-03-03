import math
from typing import List
from dungeon_tiles import Tiles
from utilities import Coordinate, Directions, debugTile, aStar

def __layoutToTile(layout_str : str):
    if layout_str == "x":
        return Tiles.WALL
    elif layout_str == "o":
        return Tiles.PATH
    elif layout_str == "D":
        return Tiles.DOOR
    else:
        return Tiles.IGNORE

matrix = '''\
o o o x o o o o o o o
o o o x o o o o o o o
o o o x x x x x x x o
o o o o o o o o o o o
o o o o o o o o o o o
o o o o o o o o o o o
'''

start = Coordinate(7,4)
end = Coordinate(4,1)

matrix = [[__layoutToTile(i) for i in line.split()] for line in matrix.splitlines()]

debugTile(matrix)

path = aStar(start,end,[],matrix,[Tiles.PATH])
debugTile(matrix,multiple_points=path)
# tiles = [matrix[i][1:4] for i in range(1,3)]
# print(tiles)