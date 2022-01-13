# Default Modules
import sys

# Licensed Modules
from typing import List, Tuple
import pygame

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tile, Tiles

class RogueLikeDefaults():
    ''' Main class that handles all the basics of the dungeon creation. 
    Extend this to use the features'''

    def __init__(self, height = 50, width = 50, grid_size = 40, fps = 5):
        '''
        @Height: Number of tiles on the Y axis
        @Width: Number of tiles on the X axis
        @Grid_Size: Size of the each tile
        @FPS: Number of times the UI will be re-drawn in a second
        '''

        self.height = height
        self.width = width

        self.grid_size = grid_size

        self.window_height = self.height * self.grid_size
        self.window_width  = self.width  * self.grid_size

        self.FPS = fps

        self.tiles : List[Tiles] = None

    def start(self) :
        '''Starts the UI and draws tiles'''
        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.window_width, self.window_height))
        self.CLOCK = pygame.time.Clock()
        self.SCREEN.fill(Color.BLACK)

        while True:
            self.CLOCK.tick(self.FPS)
            
            # Call drawing methods
            self.__drawGrid()
            self.__drawTiles()

            # Call update function for extra functions..
            self.update()  

            # Exit code
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    def __drawGrid(self):
        '''Draws the tiles every frame. Don't change this'''
        for x in range(self.width):
            for y in range(self.height):
                # Default empty tile
                tile = Tiles.EMPTY_BLOCK

                # Apply size reduction based on ratio
                tile_size = (self.grid_size/100) * tile.size_ratio 
                
                # Adjust tile locations
                tile_x = (x * self.grid_size) + (self.grid_size - tile_size) / 2
                tile_y = (y * self.grid_size) + (self.grid_size - tile_size) / 2
                
                # Draw the rect
                rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                pygame.draw.rect(self.SCREEN, tile.color, rect, 1)

    def __drawTiles(self):
        '''Draws the tiles every frame. Don't change this'''
        pass
    
    def update(self):
        '''Will be called every frame. If you want to do 
        changes dynamically in every frame, extend this function'''
        pass
