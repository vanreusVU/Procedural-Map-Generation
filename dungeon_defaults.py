# Default Modules
import sys
from typing import List

# Licensed Modules
import pygame

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tiles, Tile
from dungeon_parts import DungeonPart
from utilities import Coordinate

# Print the todo list
import todos


class RogueLikeDefaults():
    ''' 
    Main class that handles all the basics of the dungeon creation. 
    Extend this to use the features
    '''

    def __init__(self, height = 50, width = 50, grid_size = 40, fps = 1):
        '''
        :param height: Number of tiles on the Y axis
        :type height: int, optional
        :param width:  Number of tiles on the X axis
        :type width: int, optional
        :param grid_size: Size of the each tile, defaults to 40
        :type grid_size: int, optional
        :param fps: Number of times the UI will be re-drawn in a second, defaults to 1
        :type fps: int, optional
        '''        

        self.height = height
        self.width = width

        self.grid_size = grid_size

        self.window_height = self.height * self.grid_size
        self.window_width  = self.width  * self.grid_size

        self.FPS = fps

        self.dungeon_parts : List[DungeonPart] = []

        self.dungeon_tiles = [[Tiles.EMPTY_BLOCK] * self.width for _ in range(self.height)] 
        return

    def start(self) :
        ''' Starts the UI and draws tiles '''

        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.window_width, self.window_height))
        self.CLOCK = pygame.time.Clock()
        self.SCREEN.fill(Color.BLACK)

        self.begin()
        
        while True:
            self.CLOCK.tick(self.FPS)
            
            # Reset tiles 
            # (We reset everytime so that if there are any changes we can draw from the begining)
            self.resetTiles()

            # Add dungeon parts to @self.dungeon_tiles
            self.dungeonPartsToTiles()

            # Call drawing methods
            self.drawTiles()

            # Call update function for extra functions..
            self.update()  

            # Exit code
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

        return

    def drawTiles(self):
        ''' Draws the tiles every frame. Don't change this '''
        for y in range(len(self.dungeon_tiles)):
            for x in range(len(self.dungeon_tiles[y])):
                # Get tile
                tile = self.dungeon_tiles[y][x]

                # Apply size reduction based on ratio
                tile_size = (self.grid_size/100) * tile.size_ratio 
                
                # Adjust tile locations and align it to the center based on the size               
                tile_loc = Coordinate(
                    (x * self.grid_size) + (self.grid_size - tile_size) / 2,
                    (y * self.grid_size) + (self.grid_size - tile_size) / 2
                )

                # Draw the rect
                rect = pygame.Rect(tile_loc.X, tile_loc.Y, tile_size, tile_size)
                pygame.draw.rect(self.SCREEN, tile.color, rect, 1, 0)

        return

    def dungeonPartsToTiles(self):
        ''' Projects the dungeon parts onto the @self.dungeon_tiles '''
        
        for dungeon_part in self.dungeon_parts:
            tiles = dungeon_part.tiles
            
            for y in range(len(tiles)):
                for x in range(len(tiles[y])):
                    # Type casting
                    tile : Tile = tiles[y][x]
                    
                    if tile == Tiles.IGNORE:
                        '''If tile type is ignore, then don't do 
                        anything and continue to check other tiles'''
                        continue

                    # (x/y + dungeon_part.x/y) -> Relative position to World Position
                    world_loc = Coordinate(
                        (x + dungeon_part.pivot_loc.X),
                        (y + dungeon_part.pivot_loc.Y)
                    )

                    # Add the dungeon_part.tile to the self.dungeon_tiles
                    self.dungeon_tiles[world_loc.Y][world_loc.X] = tile
        return
    
    def addDungenPart(self, dungeon_part : DungeonPart):
        ''' 
        Add dungeon part to the self.dungeon_parts and then project it to the tiles

        :param dungeon_part: Dungeon part to add
        :type dungeon_part: DungeonPart
        '''       

        self.dungeon_parts.append(dungeon_part)

        # Add dungeon parts to @self.dungeon_tiles
        # We are doing this call here because room creation happens in the begin function thus
        # operations on self.dungeon_tiles would return empty without the call here (before the initial loop)
        self.dungeonPartsToTiles()

    def resetTiles(self):
        ''' Resets the tiles '''

        self.dungeon_tiles = [[Tiles.EMPTY_BLOCK] * self.width for _ in range(self.height)] 
        return

    def begin(self):
        '''Will be called once after the init'''

        return

    def update(self):
        '''Will be called every frame. If you want to do 
        changes dynamically in every frame, extend this function'''
        
        return
