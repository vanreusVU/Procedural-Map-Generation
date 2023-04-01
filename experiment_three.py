# Default Modules
import sys
import copy
import string
from typing import List
import random 

# Copyrighted Modules
import pygame

# Custom Modules
from dungeon_defaults import RogueLikeDefaults
from color_constants import Color
from dungeon_tiles import Tiles
from dungeon_parts import CustomRoom, DungeonPart, Room, Corridor, Door
from utilities import Coordinate, Directions, MinMax, SquareArea, checkAlignedBlocks, debugTile, getPercentage, isWithinBounds, percentageDifference
from path_finding import distancePythagorean
from triangulation import Edge, delaunayTriangulation

# CONSTANTS

# Chance of node will be alive from the begining
START_LIFE_CHANCE = 0.45
# Alive neighbours less than this will kill the tile
STARVE_LIMIT = 2
# Alive neighbours more than this will respawn the tile
BIRTH_LIMIT = 5
# Number of steps to apply the algorithm
NUMBER_OF_STEPS = 10

# Engine Spesifics
HEIGHT = 100
WIDTH = 100
GRID_SIZE = 5
FPS = 10
 
# Random generation seed
SEED = "YOK1RL1R"#''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
print ("CURRENT SEED:", SEED)

class Experiment3(RogueLikeDefaults):
    '''Cellular Automata'''
    
    def __init__(self):
        # Random gen seed
        random.seed(SEED)

        RogueLikeDefaults.__init__(self,
            height=HEIGHT,
            width=WIDTH,
            grid_size=GRID_SIZE,
            fps=FPS)

        self.areas : List[List[Coordinate]]= []
        self.start_locations : List[Coordinate] = []

    def startLife(self):
        for y in range(len(self.dungeon_tiles)):
            for x in range(len(self.dungeon_tiles[y])):
                if random.random() <= START_LIFE_CHANCE:
                    self.start_locations.append(Coordinate(x,y))
                    self.dungeon_tiles[y][x] = Tiles.PATH

    def begin(self):
        # Init dungeon with walls
        self.dungeon_tiles = [[Tiles.WALL] * self.width for _ in range(self.height)] 

        # Init life on tiles
        self.startLife()

        # Apply celular automata for given steps
        for i in range(NUMBER_OF_STEPS):
            self.celularAutomata()
            
            # Update the viewport
            self.SCREEN.fill(Color.BLACK)
            self.drawTiles()
            pygame.display.update()

        print("a")
        # self.createArea(Coordinate(3,2))
        self.findAreas()
        
        print(len(self.areas))
        '''for area in self.areas:
            debugTile(self.dungeon_tiles, multiple_points=area, multiple_points_mark="⛝")'''

        return

    def floodFill(self, location : Coordinate):
        area : List[Coordinate] = []
        can_check : List[Coordinate] = [location]
        self.area_tiles[location.Y][location.X] == Tiles.WALL

        while True:
            if len(can_check) == 0:
                break

            temp_check = can_check[:]
            can_check = []
            
            for loc in temp_check:
                area.append(loc)

                for dir in Directions:
                    next_step : Coordinate = loc + dir.value

                    # Problem cases
                    if not isWithinBounds(next_step, self.area_tiles) or self.area_tiles[next_step.Y][next_step.X] == Tiles.WALL:
                        continue
                    
                    if not next_step in can_check: 
                        can_check.append(next_step)

                self.area_tiles[loc.Y][loc.X] = Tiles.WALL
        
        return area
                
    def isPartOfArea(self, location : Coordinate):
        areas = []
        for i in range(len(self.areas)):
            for loc in self.areas[i]:
                if loc == location:
                    areas.append(i)
                    break
        
        return areas

    def findAreas(self):
        self.area_tiles = [[tile for tile in row] for row in self.dungeon_tiles]

        for curr_loc in self.start_locations:
            if self.area_tiles[curr_loc.Y][curr_loc.X] != Tiles.WALL:
                # area = self.createArea(curr_loc, [])
                area = self.floodFill(curr_loc)

                if len(area) > 0:
                    self.areas.append(area)
                    # debugTile(self.area_tiles)
        
        print("Finish")

    def celularAutomata(self):
        self.new_tiles = [[Tiles.WALL] * self.width for _ in range(self.height)] 

        for y in range(len(self.dungeon_tiles)):
            for x in range(len(self.dungeon_tiles[y])): 
                num_alive = self.numAliveNeighbours(Coordinate(x,y))

                '''print("Num alive:", num_alive)
                debugTile(self.dungeon_tiles, Coordinate(x,y), single_point_mark="⛝")'''

                # Alive rules
                if self.dungeon_tiles[y][x] == Tiles.PATH:
                    # Any live cell with fewer than STARVE_LIMIT live neighbours dies, as if by underpopulation.
                    if num_alive <= STARVE_LIMIT:
                        self.new_tiles[y][x] = Tiles.WALL
                    else:
                        self.new_tiles[y][x] = Tiles.PATH
                
                # Dead rules
                else:
                    # Any dead cell with STARVE_LIMIT or OVERPOP_LIMIT live neighbours becomes a live cell, as if by reproduction.
                    if num_alive >= BIRTH_LIMIT:
                        self.new_tiles[y][x] = Tiles.PATH
                    else:
                        self.new_tiles[y][x] = Tiles.WALL

        # Update the dungeon tiles
        self.dungeon_tiles = self.new_tiles
        return

    def numAliveNeighbours(self, location : Coordinate) -> int:
        ''' Returns number of alive neighbours the coordinate has

        :param location: location to check for alive neighbours
        :type location: Coordinate
        :return: number of alive neighbours
        :rtype: int
        '''        
        num_alive = 0

        for y in range(-1,2):
            for x in range(-1,2):
                # Location to check
                check_loc = location + Coordinate(x,y)
                
                # Ignore if out of bounds
                if not isWithinBounds(check_loc, self.dungeon_tiles):
                    continue
                
                # Ignore if center block
                if x == 0 and y == 0:
                    continue
                
                # Check if block is alive
                if self.dungeon_tiles[check_loc.Y][check_loc.X] == Tiles.PATH:
                    num_alive += 1
                
        return num_alive

    def update(self):
        # debugTile(self.dungeon_tiles)
        return

        

        
def main():
    ex = Experiment3()
    ex.start()

if __name__ == "__main__":
    main()
