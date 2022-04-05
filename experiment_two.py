# Default Modules
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
from utilities import Coordinate, MinMax, SquareArea, debugTile, getPercentage, isWithinBounds, percentageDifference
from path_finding import distancePythagorean
from triangulation import Edge, delaunayTriangulation

# Max number of tries to place a room
MAX_PLACEMANT_TRIES = 500

# Rooom Spesifics
NUM_ROOMS = MinMax(25,30)
ROOM_WIDTH = MinMax(8,15)
ROOM_HEIGHT = MinMax(8,15)
PARTITION_MARGIN = 10


# Engine Spesifics
HEIGHT = 80
WIDTH = 80
GRID_SIZE = 15
FPS = 10
 
# Random generation seed
SEED = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
print ("CURRENT SEED:", SEED)

class Experiment2(RogueLikeDefaults):
    '''Binary Space Partitioning, A* pathfinding, Delaunay Triangulation'''
    
    def __init__(self, num_rooms: int = 0, custom_rooms: List[CustomRoom] = []):
        '''
        @num_rooms: number of randomly generated rooms to create and place on the map.
        if set, will ignore @custom_rooms
        @custom_rooms: custom rooms to place on the map
        
        '''

        # Random gen seed
        random.seed(SEED)

        RogueLikeDefaults.__init__(self,
            height=HEIGHT,
            width=WIDTH,
            grid_size=GRID_SIZE,
            fps=FPS)

        # Setting up room settings
        self.num_rooms = random.randint(NUM_ROOMS.MIN, NUM_ROOMS.MAX)
        self.custom_rooms = custom_rooms
        self.triangulation = []

        # Possible locatations to place rooms
        self.possible_room_areas : List[SquareArea] = []
        

    def binarySpacePartitioning(self, area : SquareArea):
        '''
        Is a method for recursively subdividing a space into two convex sets by using hyperplanes as partitions.

        :param area: Area to devide
        :type area: SquareArea
        '''        

        rect = pygame.Rect(area.location.X * GRID_SIZE, area.location.Y * GRID_SIZE,area.width * GRID_SIZE,area.height* GRID_SIZE)
        pygame.draw.rect(self.SCREEN, Color.RED, rect, 1, 0)
        pygame.display.update()
        pygame.time.delay(100)

        # Check if the area fits to be a room.
        # + percentage is for leaving more space for room movement
        if area.height <= ROOM_HEIGHT.MAX + getPercentage(ROOM_HEIGHT.MAX, 30) and area.width <= ROOM_WIDTH.MAX + getPercentage(ROOM_WIDTH.MAX, 30):
            # Add this area as a possible room
            self.possible_room_areas.append(area)
            return

        # 0 = Vertical, 1 = Horizontal 
        split_decision = random.randint(0,1)
        
        # If partitians are too wide or long
        if percentageDifference(area.height, area.width) >= 25:
            area.child_squares = area.splitHorizontally(25)
        elif percentageDifference(area.width, area.height) >= 25:
            area.child_squares = area.splitVertically(25)
        # If not go with the random splitting
        else:
            # Also check if spliting the room will end up with too tiny rooms
            if split_decision == 1:
                area.child_squares = area.splitHorizontally(25)
            else:
                area.child_squares = area.splitVertically(25)

        # Partition the child areas
        for square in area.child_squares:
            self.binarySpacePartitioning(square)

        
    def createRooms(self):
        ''' Create rooms '''
        # Number of tries
        tries = 0
        rooms_created = 0

        # Create a area of the dungteon_tiles
        whole_map : SquareArea = SquareArea(
            Coordinate(0,0),
            self.width,
            self.height
        )

        # Apply BSP to partition the map into smaller areas
        self.binarySpacePartitioning(whole_map)

        pygame.time.delay(5000)
        # Place rooms until enough rooms have been placed.
        # Will try to place a room @MAX_PLACEMANT_TRIES times and if it's still not a sucess it will 
        # stop placing rooms. The @tries gets reseted after every successfull placement.
        while rooms_created < self.num_rooms and tries < MAX_PLACEMANT_TRIES:
            # Get a random area
            room_area : SquareArea = random.choice(self.possible_room_areas)
            
            # Skip if the partitian is too small for placement. We need the room_width to me 2 tile bigger than the
            # room_width.min so that we can leave empty spaces around the room for corridors
            if room_area.width < ROOM_WIDTH.MIN + 2 or room_area.height < ROOM_HEIGHT.MIN + 2 :
                continue

            # We want the room to be within the area and leave a empty line around the border
            # Thats why we deduct 2 from the room's size (one from begining, one from end)
            r_width = random.randint(ROOM_WIDTH.MIN, min(room_area.width, ROOM_WIDTH.MAX) - 2)
            r_height = random.randint(ROOM_HEIGHT.MIN, min(room_area.height, ROOM_HEIGHT.MAX) - 2)

            # Get random location within the partition
            r_x = room_area.location.X + random.randint(1, (room_area.width - r_width) - 1)
            r_y = room_area.location.Y + random.randint(1, (room_area.height - r_height) - 1)

            # +1 is for avoiding clashing walls
            rand_room = Room(r_x, r_y, r_height, r_width)
            
            # Increase the number of tries
            tries += 1

            # Add the created room if it's placeable
            if self.canPlace(rand_room) == True:
                self.addDungenPart(rand_room)
                rooms_created += 1

                # Reset the number of tries
                tries = 0

        # Update the rooms
        for part in self.dungeon_parts:
            if isinstance(part,Room):
                part.afterInit(self.dungeon_tiles)

        # Update the viewport
        self.drawTiles()
        pygame.display.update()

    def matchCoordinateWithRoom(self, coord : Coordinate) -> Room:
        '''
        Returns the room with the given pivot location

        :param coord: pivot_location of the room
        :type coord: Coordinate
        :return: Room with the given location
        :rtype: Room
        '''        

        # Find all the rooms with the given pivot
        rooms = [room for room in self.dungeon_parts if isinstance(room, Room) and room.pivot_loc == coord]

        if len(rooms) > 1:
            print("ERROR: Multiple rooms with same pivot")
        
        if len(rooms) == 0:
            print("WARNING: No rooms with given location")
            return None

        return rooms[0]
        
    def findRoomConnections(self):
        ''' Decide on the routes to be connected '''
        
        # Chance of loop connection
        chance_of_loop = 0.2

        # Adjust the room cordinates based on the grid size
        room_coordinates : List[Coordinate] = [Coordinate(part.pivot_loc.X, part.pivot_loc.Y) for part in self.dungeon_parts if isinstance(part, Room)]
        # Form a delaunay triangulation from the room locations
        self.triangulation = delaunayTriangulation(room_coordinates)

        # Extract all the edges from the triangulation
        all_edges : List[Edge] = []
        for triangle in self.triangulation:
            for edge in triangle.edges:
                if edge not in all_edges:
                    all_edges.append(edge)

        # Visited verticies
        visited : List[Coordinate] = [room_coordinates[0]]
        # Shortest spanning tree
        self.paths : List[Edge] = []

        # We use Prim's Algorithm to find the minnimum spanning tree in delaunay triangulation
        # https://en.wikipedia.org/wiki/Prim%27s_algorithm
        while(len(visited) < len(room_coordinates)):
            # Potential paths to be taken from visited nodes
            potential_paths : List[Edge] = []
            # If true next path might be a loop too (without crossing the same path)
            is_loop_allowed = random.random() < chance_of_loop

            # Find reachable verticies from the visited nodes and calculate their distances
            for edge in all_edges:
                # Check if the verticies in the edges are visited
                vert1_in = edge.p1 in visited
                vert2_in = edge.p2 in visited

                # If both sides of the edge isn't visited
                if vert1_in != vert2_in:
                    # Potential path p1: visited vertex p2: unvisited vertex
                    potential_path = Edge(edge.p2, edge.p1) if vert1_in is False else Edge(edge.p1, edge.p2)
                
                    # Add the potential_path to the potential_paths
                    potential_paths.append(potential_path)
                
                # If both sides are visited the path will be counted if random number is less than chance_of_loop
                # With this we can add some variaty to the dungeon by adding loops
                elif any([vert1_in, vert2_in]) and is_loop_allowed:
                    if not edge in self.paths:
                        # Add the current edge to the potential_paths
                        potential_paths.append(edge)

            # If no path is available
            if len(potential_paths) == 0:
                print("No potential path exists")
                break

            # Init the cheapest path
            cheapest_path = potential_paths[0]
            cheapest_path_distance = distancePythagorean(cheapest_path.p1, cheapest_path.p2)
            
            # Find the  cheapest path
            for potential_path in potential_paths:
                distance = distancePythagorean(potential_path.p1, potential_path.p2)
                
                if distance < cheapest_path_distance:
                    cheapest_path = potential_path  

            # Add the p1 of the cheapest path to visited verticies list if its not already visited
            # In a case of loop don't add the vertex as visited again    
            if not cheapest_path.p2 in visited:
                visited.append(cheapest_path.p2)

            # Add the result to paths list
            self.paths.append(cheapest_path)
        
    def drawRoomConnections(self):
        ''' Draw room connections '''

        for triangle in self.triangulation:
            for edge in triangle.edges:
                # Adjust the locations based on the grid to draw them properly
                p1 = (edge.p1.X * GRID_SIZE, edge.p1.Y * GRID_SIZE)
                p2 = (edge.p2.X * GRID_SIZE, edge.p2.Y * GRID_SIZE)

                pygame.draw.line(self.SCREEN, Color.RED, p1, p2, 3)

        for edge in self.paths:
            # Adjust the locations based on the grid to draw them properly
            p1 = (edge.p1.X * GRID_SIZE, edge.p1.Y * GRID_SIZE)
            p2 = (edge.p2.X * GRID_SIZE, edge.p2.Y * GRID_SIZE)
            
            pygame.draw.line(self.SCREEN, Color.LIME, p1, p2, 3)

            pygame.draw.circle(self.SCREEN , Color.WHITE, p1, 5)
            pygame.draw.circle(self.SCREEN , Color.WHITE, p2, 5)
        
        pygame.display.update()
 
    def createCorridors(self):
        ''' Creates corridors '''
        
        for path in self.paths:
            rooms : List[Room] = (self.matchCoordinateWithRoom(path.p1), self.matchCoordinateWithRoom(path.p2))
            
            # Check if all the rooms are found
            if None in rooms:
                print("ERROR: Can't find one of the rooms")
                return

            # Since the tile checks on the pathfinding algorithm are based on dungeon 
            # tiles we need to write the doors onto the tiles
            self.dungeonPartsToTiles()

            corridor = Corridor(rooms[0].getCenter(), rooms[1].getCenter(), self.dungeon_tiles, False)

            self.addDungenPart(corridor)

        # Update the rooms
        for part in self.dungeon_parts:
            if isinstance(part,Corridor):
                part.afterInit(self.dungeon_tiles)

        # Update the viewport
        self.drawTiles()
        pygame.display.update()

    def canPlace(self, part_to_place: DungeonPart) -> bool:
        '''
        Checks if a DungeonPart can be placed to the given @x, @y location
        '''
        dp_tiles = part_to_place.tiles

        for y in range(len(dp_tiles)):
            for x in range(len(dp_tiles[y])):
                # (x/y + dungeon_part.x/y) -> Relative position to World Position
                world_x = x + part_to_place.pivot_loc.X
                world_y = y + part_to_place.pivot_loc.Y
                
                # If outside of map bounds
                if isWithinBounds(Coordinate(world_x, world_y),self.dungeon_tiles) == False:
                    return False

                # If its a none essentail block, skip this iter
                if dp_tiles[y][x] == Tiles.IGNORE or dp_tiles[y][x] == Tiles.EMPTY_BLOCK:
                    continue
                
                # If there
                if self.dungeon_tiles[world_y][world_x] != Tiles.EMPTY_BLOCK:
                    return False
        
        return True  

    def begin(self):
        # Create the rooms
        self.createRooms() 

        # Wait a little
        pygame.time.delay(500)

        # Make connections
        self.findRoomConnections()

        # Draw room connections
        self.drawRoomConnections()

        # Create the corridors
        self.createCorridors()

        # Wait a little
        pygame.time.delay(500)

        # Erase the lines
        self.SCREEN.fill(Color.BLACK)

        return

    def update(self):
        return
        
def main():
    ex = Experiment2(NUM_ROOMS)
    ex.start()

if __name__ == "__main__":
    main()
