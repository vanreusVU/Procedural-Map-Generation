# Default Modules
import sys
from typing import List

# Licensed Modules
import pygame

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tiles, Tile
from dungeon_parts import DungeonPart

class RogueLikeDefaults():
    ''' Main class that handles all the basics of the dungeon creation. 
    Extend this to use the features'''

    def __init__(self, height = 50, width = 50, grid_size = 40, fps = 1):
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

        self.dungeon_parts : List[DungeonPart] = []

        self.tiles = [[Tiles.EMPTY_BLOCK] * self.width for _ in range(self.height)] 
        return

    def start(self) :
        '''Starts the UI and draws tiles'''
        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.window_width, self.window_height))
        self.CLOCK = pygame.time.Clock()
        self.SCREEN.fill(Color.BLACK)

        while True:
            self.CLOCK.tick(self.FPS)
            
            # Reset tiles 
            # (We reset everytime so that if there are any changes we can draw from the begining)
            self.resetTiles()

            # Add dungeon parts to @self.tiles
            self.__dungeonPartsToTiles()

            # Call drawing methods
            self.__drawTiles()

            # Call update function for extra functions..
            self.update()  

            # Exit code
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

        return

    def __drawTiles(self):
        '''Draws the tiles every frame. Don't change this'''
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                # Get tile
                tile = self.tiles[x][y]

                # Apply size reduction based on ratio
                tile_size = (self.grid_size/100) * tile.size_ratio 
                
                # Adjust tile locations and align it to the center based on the size
                tile_x = (x * self.grid_size) + (self.grid_size - tile_size) / 2
                tile_y = (y * self.grid_size) + (self.grid_size - tile_size) / 2
                
                # Draw the rect
                rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                pygame.draw.rect(self.SCREEN, tile.color, rect, 1, 0)

        return

    def __dungeonPartsToTiles(self):
        '''Projects the dungeon parts onto the @self.tiles'''
        
        for dungeon_part in self.dungeon_parts:
            tiles = dungeon_part.tiles
            
            for x in range(len(tiles)):
                for y in range(len(tiles[0])):
                    # Type casting
                    tile : Tile = tiles[x][y]
                    
                    if tile == Tiles.IGNORE:
                        '''If tile type is ignore, then don't do 
                        anything and continue to check other tiles'''
                        continue

                    # (x/y + dungeon_part.x/y) -> Relative position to World Position
                    tile_x = (x + dungeon_part.x) 
                    tile_y = (y + dungeon_part.y)

                    # Add the dungeon_part.tile to the self.tiles
                    self.tiles[tile_x][tile_y] = tile



        return
    
    def addDungenPart(self, dungeon_part : DungeonPart):
        ''' Add dungeon part to the self.dungeon_parts '''
        self.dungeon_parts.append(dungeon_part)

    def resetTiles(self):
        self.tiles = [[Tiles.EMPTY_BLOCK] * self.width for _ in range(self.height)] 
        return

    def update(self):
        '''Will be called every frame. If you want to do 
        changes dynamically in every frame, extend this function'''
        return
