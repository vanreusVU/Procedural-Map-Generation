# Default Modules
import sys

# Licensed Modules
from typing import List, Tuple
import pygame

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tile, Tiles

class RogueLikeDefaults():

    def __init__(self, height = 50, width = 50, grid_size = 40, fps = 5):
        self.height = height
        self.width = width

        self.grid_size = grid_size

        self.window_height = self.height * self.grid_size
        self.window_width  = self.width  * self.grid_size

        self.FPS = fps

        self.tiles : List[List[Tile]]= [[Tiles.EMPTY_BLOCK] * width for _ in range(height)]

    def start(self) :
        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.window_width, self.window_height))
        self.CLOCK = pygame.time.Clock()
        self.SCREEN.fill(Color.BLACK)

        while True:
            self.CLOCK.tick(self.FPS)
            self.__drawGrid()
            self.drawDungeon()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    def __drawGrid(self):
        for x in range(self.width):
            for y in range(self.height):
                tile = self.tiles[x][y]
                tile_size = (self.grid_size/100) * tile.size_ratio 

                tile_x = (x * self.grid_size) + (self.grid_size - tile_size) / 2
                tile_y = (y * self.grid_size) + (self.grid_size - tile_size) / 2
                
                rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                pygame.draw.rect(self.SCREEN, tile.color, rect, 1)

        '''for x in range(0, self.window_width, self.grid_size):
            for y in range(0, self.window_height, self.grid_size):
                block_pos_x = x + (self.grid_size - self.empty_block_size) / 2
                block_pos_y = y + (self.grid_size - self.empty_block_size) / 2
                rect = pygame.Rect(block_pos_x, block_pos_y, self.empty_block_size, self.empty_block_size)
                pygame.draw.rect(self.SCREEN, Color.WHITE, rect, 1)'''


    def drawRectangle(self, x: int, y: int, width: int, height: int, color: Tuple = Color.WHITE):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.SCREEN, color, rect, 1)

    def drawDungeon(self):
        pass