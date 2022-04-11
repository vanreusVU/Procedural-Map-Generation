# Default Modules
from typing import List
from random import randrange
import copy

# Custom Modules
from color_constants import Color
from dungeon_tiles import Tile, Tiles
from utilities import Coordinate, checkAlignedBlocks, debugTile, globalToRelative, isWithinBounds
from path_finding import aStar

class DungeonPart():
    '''
    Parent dungeon part class.
    Contains the neccesary variables needed to draw the DungeonParts in 
    <dungeon_defaults.py>.RogueLikeDefaults.__drawDungeonParts()
    '''

    def __init__(self, x : int, y : int) -> None:
        '''Just crates the template variables

        :param x: world position of the object in X axis
        :type x: int
        :param y: world position of the object in Y axis
        :type y: int
        '''        
        
        # Location of the pivot point (upper left corner)
        # This will be used to align the parts location on the grid
        self.pivot_loc = Coordinate(x,y)

        # Tiles of the dungeon part. Mark the empty parts as Tiles.Ignore
        self.tiles : List[List[Tile]] = []
        return

    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''
        Call this after creating the dungen_parts if you want to make any changes after the main init
        Example in @Room Class with <experiment_one.py>
        '''
        return

class Door():
    '''A simple door object'''
    def __init__(self, x: int, y: int):
        '''
        :param x: relative location of the pivot (top left corner) of the room
        :type x: int
        :param y: relative location of the pivot (top left corner) of the room
        :type y: int
        '''        

        self.location = Coordinate(x,y)

class Room(DungeonPart):
    '''
    Creates a room from the given @height, @width, @color.
    Pivot point is top left corner.
    '''

    # Max amount of tries to place a door
    MAX_DOOR_PLACEMENT_TRIES = 500

    def __init__(self, x: int, y: int, height: int, width: int, wall_color: Color = None):
        '''
        :param x: world position of the object in X axis
        :type x: int
        :param y: world position of the object in Y axis
        :type y: int
        :param height: heightof the room in tiles
        :type height: int
        :param width: width of the room in tiles
        :type width: int
        :param wall_color: overrides the Tiles.Wall's default color., defaults to None
        :type wall_color: Color, optional
        '''        
        
        DungeonPart.__init__(self, x, y)
        
        # Size info
        self.height = height
        self.width = width

        # Color
        self.color = wall_color

        # Create the room tiles
        # Where the corner pieces are Tiles.WALL and inner pieces are Tiles.PATH
        self.tiles = [[Tiles.WALL] * self.width for _ in range(self.height)]
        for y in range(1,self.height - 1):
            self.tiles[y][1: self.width - 1] = [Tiles.PATH] * (self.width - 2) 
        
        # Quick access for the doors.
        self.doors : List[Door] = []

        return

    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''
        Part of DungeonPart
        Load dungeon tiles

        :param dungeon_tiles: Global dungeon tiles
        :type dungeon_tiles: List[List[Tiles]]
        '''
        
        # Assign dungeon tiles
        self.dungeon_tiles = dungeon_tiles

    def addDoor(self, location : Coordinate):
        ''' Adds a door to the given relative loation at the room

        :param location: relative location to place a door at
        :type location: Coordinate
        '''        

        # Check if the same door exists
        for door in self.doors:
            if door.location == location:
                # Door already exists
                return

        # Add the door
        self.doors.append(Door(location.X, location.Y))
        self.tiles[location.Y][location.X] = Tiles.DOOR

    def getCenter(self) -> Coordinate:
        ''' Get the world center of the room

        :return: Center of the room 
        :rtype: Coordinate
        '''        
        x = int(self.width/2) + self.pivot_loc.X
        y = int(self.height/2) + self.pivot_loc.Y

        return Coordinate(x,y)

    def __loadDoors(self):
        '''
        Goes through the @self.tiles and crates Door object for each of the doors.
        Appends to self.doors
        '''

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x] == Tiles.DOOR:
                    self.doors.append(Door(x,y))
    
    def canPlaceDoor(self, x : int, y : int) -> bool:
        '''
        Checks if the door is placeable at the given location.
        Avoids placing doors on corner pieces, next to each other and places where the door will be blocked


        To wall piece to not be a corner. It should have continuing pieces either along the x or y axis
        C = piece to check
        o = empty/none blocking tile
        x = wall tile

        Not corner cases:
        case 1:          case 2:
            o x o           o o o
            o C o           x C x
            o x o           o o o

        Corner case:
        case 1:
            o x o          
            o C x         
            o o o         

        :param x: relative location to check
        :type x: int
        :param y: relative location to check
        :type y: int
        :return: if the door is placeable at the given location.
        :rtype: bool
        '''        

        # Check if the door is being blocked by another dungeon tile and also for corner pieces
        world_aligned = checkAlignedBlocks(Coordinate(x + self.pivot_loc.X, y + self.pivot_loc.Y), self.dungeon_tiles, Tiles.BLOCKING_TILES, True)
        world_check = (world_aligned.X == 2 and world_aligned.Y == 0) or (world_aligned.Y == 2 and world_aligned.X == 0)
        
        # Check if the door is next to another door
        door_aligned = checkAlignedBlocks(Coordinate(x, y), self.tiles, [Tiles.DOOR], False)
        door_check = door_aligned.X + door_aligned.Y == 0

        return world_check and door_check


    def getWallTileLocations(self, room) -> List[Coordinate]:
        '''
        Returns an array of all the room locations of the given room

        :param room: Room to get the walls locations of
        :type room: Room
        :return: List of wall locations
        :rtype: List[Coordinate]
        '''        
        
        wall_locations : List[Coordinate] = []
        
        # Type casting
        room : Room = room

        for y in range(len(room.tiles)):
            for x in range(len(room.tiles[y])):
                if room.tiles[y][x] == Tiles.WALL:
                    wall_locations.append(Coordinate(x,y))

        return wall_locations

    def createRandomDoor(self) -> Door:
        '''
        Creates doors on random locations around the walls based on the @self.num_rooms
        '''
        # Number of tries
        tries = 0

        # Created door
        door : Door = None

        # Get all the wall locations and index them by adding them to an array
        wall_locations : List[Coordinate] = self.getWallTileLocations(self)

        # Select random door locations
        while (tries < self.MAX_DOOR_PLACEMENT_TRIES):
            random_loc = randrange(0, len(wall_locations))
            check_loc = wall_locations[random_loc]
  
            # Don't add door if the door is not placable or a door is already added to that location
            if (self.canPlaceDoor(check_loc.X,check_loc.Y) == False or self.tiles[check_loc.Y][check_loc.X] == Tiles.DOOR):
                tries += 1
                continue
            
            # Add door
            door = Door(check_loc.X,check_loc.Y)
            self.doors.append(door)
            self.tiles[check_loc.Y][check_loc.X] = Tiles.DOOR

            # Door placed, exit the loop
            break

        # Load doors from the self.tiles
        self.__loadDoors()
        return door

class CustomRoom(Room):
    '''
    A room where you create your custom room by giving the room scheme as input
    '''

    def __init__(self, x: int, y: int, room_layout : str):
        '''
        x = wall
        o = walkable area
        D = Door

        :param x: world position of the object in X axis
        :type x: int
        :param y: world position of the object in Y axis
        :type y: int
        :param room_layout: room's layout in string. See the example below
        :type room_layout: str
        '''        
       
        example_room_layout = '''\
        x x x x
        x o o x
        x o o D
        x x x x
        '''
        DungeonPart.__init__(self, x, y)

        # Seperates the string into 2d array and crates a new array based on the values 
        self.tiles = [[self.__layoutToTile(i) for i in line.split()] for line in room_layout.splitlines()]
        
        # Quick access for the doors.
        self.doors = []
        # Load doors from the self.tiles
        self.__loadDoors()

        return

    def __layoutToTile(self, layout_str : str) -> Tile:
        '''
        Converts the string layout elements to Tiles
        x = wall
        o = walkable area
        D = Door

        :param layout_str: multi line string
        :type layout_str: str
        :return: Tile equivalent of the string
        :rtype: Tile
        '''        

        if layout_str == "x":
            return Tiles.WALL
        elif layout_str == "o":
            return Tiles.PATH
        elif layout_str == "D":
            return Tiles.DOOR
        else:
            return Tiles.IGNORE

class Corridor(DungeonPart):
    '''
    Base class to create corridors from the given @start_room to @end_room by using the A* pathfinding algorithm.
    '''

    def __init__(self, start_room : Room, end_room : Room, dungeon_tiles: List[List[Tiles]], color: Color = None):
        '''
        :param start: First room
        :type start: Room
        :param end: Connected room
        :type end: Room
        :param start: should avoid walls or not, default to True
        :type start: Bool, optional
        :param color: overrides the Tiles default color., defaults to None
        :type color: Color, optional
        '''        
        DungeonPart.__init__(self, 0, 0)

        # Location info
        # Start position
        self.start_room : Room = start_room

        # End position
        self.end_room : Room = end_room

        # Assign dungeon tiles
        self.dungeon_tiles = dungeon_tiles

        # Adjust tiles size
        self.tiles = [[Tiles.IGNORE] * len(self.dungeon_tiles[0]) for _ in range(len(self.dungeon_tiles))]

        # Create the corridor
        self.createCorridor()
    
    def afterInit(self, dungeon_tiles: List[List[Tiles]]):
        '''
        Part of DungeonPart
        In this case add doors to the room

        :param dungeon_tiles: Global dungeon tiles
        :type dungeon_tiles: List[List[Tiles]]
        '''    

        # Update dungeon tiles
        self.dungeon_tiles = dungeon_tiles

        # Place the corridor onto tile
        self.placeCorridor()

    def isWithinRoom(self, x: int, y: int, room: Room) -> bool:
        '''is the location within the bounds of the given room

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :param room: room to check
        :type room: Room
        :return: True if the coordinate is within the room
        :rtype: bool
        '''     

        within_x = x >= room.pivot_loc.X and x < room.pivot_loc.X + room.width 
        within_y = y >= room.pivot_loc.Y and y < room.pivot_loc.Y + room.height

        return within_x and within_y

    def isWithinRooms(self, x: int, y: int) -> bool:
        ''' is the location within the starting or ending room

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :return: is the location within the starting or ending room
        :rtype: bool
        '''        
        return self.isWithinRoom(x,y,self.start_room) or self.isWithinRoom(x,y,self.end_room)

    def removeRoomPieces(self, room : Room):
        ''' Remove all room pieces except the corner pieces. Used to make astar alogirthm work properly

        :param room: Room the be removed
        :type room: Room
        '''        

        for y in range(len(room.tiles)):
            for x in range(len(room.tiles[y])):
                relative_alignment = checkAlignedBlocks(Coordinate(x, y), room.tiles, Tiles.BLOCKING_TILES, False)

                # If the tile is not a corner piece remove it from self.dungeon_tiles
                if (relative_alignment.X == 2 and relative_alignment.Y == 0) or (relative_alignment.Y == 2 and relative_alignment.X == 0):
                    self.dungeon_tiles[room.pivot_loc.Y + y][room.pivot_loc.X + x] = Tiles.SOFT_IGNORE_WALL

    def adjustCorridorPath(self) -> List[Coordinate]:
        ''' 
        Remove parts of the corridor that overlaps with the inital rooms (start, end). Return the endpoints of the corridor

        :return: end points of overlap with the rooms, could be used to place doors at
        :rtype: List[Coordinate]
        '''                   

        # Adjusted path
        path : List[Coordinate] = []
        
        # Edge points are the only overlaps that the corridor has with the rooms -> the doors
        edge_points : List[Coordinate] = [None, None]

        # Cut the corridor from start rooms wall to ending rooms wall
        for coord in self.corridor_path: 
            if not self.isWithinRooms(coord.X, coord.Y):
                path.append(coord)

        for coord in self.corridor_path:
            if self.isWithinRoom(coord.X, coord.Y, self.start_room):
                edge_points[0] = coord
            if self.isWithinRoom(coord.X, coord.Y, self.end_room):
                edge_points[1] = coord
                # We want to first tile within the room for the door.
                # Thats why we break out after finding it
                break

        # debugTile(self.dungeon_tiles, multiple_points=edge_points, multiple_points_mark="⛝")

        self.corridor_path = path

        return edge_points

    def createDoorAtRoom(self, door_location : Coordinate, room : Room):
        '''
        Add door to the given room

        :param door_location: global_door_location
        :type door_location: Coordinate
        :param room: room to add the door to
        :type room: Room
        '''        

        relative_location : Coordinate = globalToRelative(room.pivot_loc, door_location)
        if isWithinBounds(relative_location, room.tiles) == False:
            print("ERROR: createDoorAtRoom, relative location is out of bounds", relative_location)
            debugTile(self.dungeon_tiles, single_point=door_location, single_point_mark="⛝")
            return

        # Add door
        room.addDoor(relative_location)

    def createCorridor(self):
        '''
        Gets called during __init__
        Extend this create the corridor by filling its shape in @self.tiles
        '''
    
        # Remove start and end rooms from the tiles for the astar so that it will ignore the both of the rooms
        # However, keep the corner pieces in because we don't want connection from corner pieces
        self.removeRoomPieces(self.start_room)
        self.removeRoomPieces(self.end_room)

        # Get the corridor path
        self.corridor_path = aStar(self.start_room.getCenter(), self.end_room.getCenter(), [], self.dungeon_tiles)
        
        # self.corridor_path = [path for path in temp_corridor_path if self.isWithinRooms(path.X, path.Y) == False]

        # Clean path and get room locations
        end_points = self.adjustCorridorPath()

        # debugTile(self.dungeon_tiles, multiple_points=self.corridor_path, multiple_points_mark="⛝")
    
        if len(end_points) == 0:
            print("ERROR: No end points")

        # Create doors at rooms
        self.createDoorAtRoom(end_points[0], self.start_room)
        self.createDoorAtRoom(end_points[1], self.end_room)

        if self.corridor_path == None:
            print("Couldn't reach the destination")
            return 

        # Place Tiles to the given coordiantes
        for coord in self.corridor_path:
            self.tiles[coord.Y][coord.X] = Tiles.PATH

    def placeCorridor(self):
        # Place Tiles to the given coordiantes
        for coord in self.corridor_path:

            # Basically place walls around the path
            for y in range(-1,2):
                for x in range(-1,2):
                    if x == 0 and y == 0:
                        continue
                    
                    coord_to_place = Coordinate(x + coord.X,y + coord.Y)
                    if isWithinBounds(coord_to_place ,self.dungeon_tiles) == True:
                        # We need to check both the local tiles and world tiles to be sure we are not overwriting anything
                        # because the changes in the local tiles aren't transfered to the global untill the next tick

                        # Check if the block in global is empty
                        if self.dungeon_tiles[coord_to_place.Y][coord_to_place.X] == Tiles.EMPTY_BLOCK:
                            # Check if the block in local is not PATH
                            if self.tiles[coord_to_place.Y][coord_to_place.X] == Tiles.IGNORE:
                                self.tiles[coord_to_place.Y][coord_to_place.X] = Tiles.WALL

