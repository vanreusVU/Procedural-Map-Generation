# Default Modules
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
from utilities import Coordinate, MinMax, debugTile
from path_finding import distancePythagorean
from triangulation import Edge, delaunayTriangulation

# Max number of tries to place a room
MAX_PLACEMANT_TRIES = 500

NUM_ROOMS = MinMax(15,25)
ROOM_WIDTH = MinMax(4,10)
ROOM_HEIGHT = MinMax(4,10)
ROOM_DOOR = MinMax(1,2)

HEIGHT = 80
WIDTH = 80
GRID_SIZE = 15
FPS = 10

# Random generation seed
SEED = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
print ("CURRENT SEED:", SEED)

class SimpleRoomPlacement(RogueLikeDefaults):
    '''Simple Room Placement Algorithm for random dungeon generation'''
    
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
        

    def createRooms(self):
        ''' Create rooms '''
        # Number of tries
        tries = 0
        rooms_created = 0

        # Place rooms until enough rooms have been placed.
        # Will try to place a room @MAX_PLACEMANT_TRIES times and if it's still not a sucess it will 
        # stop placing rooms. The @tries gets reseted after every successfull placement.
        while rooms_created < self.num_rooms and tries < MAX_PLACEMANT_TRIES:
            r_width = random.randint(ROOM_WIDTH.MIN, ROOM_WIDTH.MAX)
            r_height = random.randint(ROOM_HEIGHT.MIN, ROOM_HEIGHT.MAX)
            
            r_x = random.randint(0, (self.width - r_width))
            r_y = random.randint(0, (self.height - r_height))

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
            
            pygame.draw.line(self.SCREEN, Color.YELLOW, p1, p2, 3)

            # pygame.draw.circle(self.SCREEN , Color.WHITE, triangle.pivot_vertex.getTuple(), 5)
 
    def createCorridors(self):
        ''' Creates corridors '''
        

        for path in self.paths:
            rooms : List[Room] = (self.matchCoordinateWithRoom(path.p1), self.matchCoordinateWithRoom(path.p2))
            doors : List[Door] = []
            
            # Check if all the rooms are found
            if None in rooms:
                print("ERROR: Can't find one of the rooms")
                return

            # Create door for the rooms
            for room in rooms:
                door = room.createRandomDoor()

                if door == None:
                    print("WARNING: Can't connect to the created door")
                    # If room can't be created check if there are any doors that can be used
                    if len(room.doors) > 0:
                        door = room.doors[len(room.doors) - 1]
                    else:
                        print("ERROR: No door to connect")
                        return                
                    
                # Add door to the list
                doors.append(door)

            # Since the tile checks on the pathfinding algorithm are based on dungeon 
            # tiles we need to write the doors onto the tiles
            self.dungeonPartsToTiles()

            door1_world_loc = doors[0].location + rooms[0].pivot_loc
            door2_world_loc = doors[1].location + rooms[1].pivot_loc
            corridor = Corridor(door1_world_loc, door2_world_loc, self.dungeon_tiles)

            self.addDungenPart(corridor)

        # Update the rooms
        for part in self.dungeon_parts:
            if isinstance(part,Corridor):
                part.afterInit(self.dungeon_tiles)

        


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
        
        # Make connections
        self.findRoomConnections()

        # Draw room connections
        self.drawRoomConnections()

        # Create the corridors
        self.createCorridors()
        return

    def update(self):
        return
        
def main():
    srp = SimpleRoomPlacement(NUM_ROOMS)
    srp.start()

if __name__ == "__main__":
    main()
