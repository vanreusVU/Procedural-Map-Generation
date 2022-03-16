import math
from typing import List
from dungeon_tiles import Tiles
from utilities import Coordinate, Directions, isWithinBounds

class Node():
    ''' A class that represents the nodes in a tile map to be used for A* pathfinding algorithm '''

    def __init__(self, location : Coordinate, g_cost : float = None, h_cost : float = None):
        # Coordinates of the current node
        self.location = location
        
        # Cost of the current node
        self.g_cost : float = g_cost 
        self.h_cost : float = h_cost

        self.coming_from : Node = None
        
        if g_cost == None or h_cost == None:
            self.f_cost : float = None
        else:
            self.f_cost : float = g_cost + h_cost

        # Costs of the neighbours
        self.neighbours : List[Node] = None
        pass

def distanceTriangulate(location : Coordinate, goal : Coordinate):
    ''' 
    Gets the triangular straight distance between 
    Example:
    x x x S
    x o o o
    x o o o
    G o o o

    S = Start
    G = Goal 
    x = calculation path
    distance = 6 (jumps betwen nodes)

    returns distance in int
    '''

    return abs(location.X - goal.X) + abs(location.Y - goal.Y)

def distancePythagorean(location : Coordinate, goal : Coordinate):
    ''' 
    Gets the triangular pythagorean distance
    Example:
    o o o S
    o o p o
    o p o o
    G o o o

    S = Start
    G = Goal 
    p = calculation path
    distance = 5.66

    returns distance in float
    '''

    x = abs(location.X - goal.X)
    y = abs(location.Y - goal.Y)

    return math.sqrt(math.pow(x,2) + math.pow(y,2))
    
def shouldFollowTile(location : Coordinate, tiles : List[List[Tiles]], tiles_to_follow : List[Tiles]):
    '''
    Checks if the tile at the given location is a part of tiles_to_follow
    '''

    if isWithinBounds(location, tiles) == False:
        return False

    return tiles[location.Y][location.X] in tiles_to_follow

def isNodeTraversed(location : Coordinate, steps : List[Node]):
    # Check if the location is already been traversed
    for node in steps:
        if location.X == node.location.X and location.Y == node.location.Y:
            return True

    return False

def aStar(curr : Coordinate, goal : Coordinate, steps : List[Node], tiles : List[List[Tiles]], tiles_to_follow : List[Tiles]) -> List[Coordinate]:
    '''
    Gets the shorthest path between curr and goal by using A* Pathfinding algorithm.
    '''
    # Copy the lists
    steps = steps[:]

    # Add the starting node
    if len(steps) == 0:
        steps.append(Node(curr))
    
    # Check if its the goal
    if curr.X == goal.X and curr.Y == goal.Y:
        current_node = steps[len(steps) - 1]
        shorthest_path = [current_node.location]

        while current_node.coming_from != None:
            shorthest_path.insert(0, current_node.coming_from.location)
            current_node = current_node.coming_from

        return shorthest_path

    # List of nodes nodes. F_cost = (sum of g_cost and h_cost) * 10. the algorithm will be using this to determin which path to take
    neighbours : List[Node] = []

    for dir in Directions:
        dir_name = dir.name
        dir : Coordinate = dir.value

        loc_to_check = Coordinate(curr.X + dir.X, curr.Y + dir.Y)

        # Skip if the current location is out of bounds or filtered out
        if isWithinBounds(loc_to_check, tiles) == False or shouldFollowTile(loc_to_check,tiles,tiles_to_follow) == False:
            continue 
        
        # Check if the location is already been traversed
        if isNodeTraversed(loc_to_check,steps) == True:
            continue

        # distance from starting node
        g_cost = distanceTriangulate(loc_to_check,steps[0].location) * 10
        # distance from the end node
        h_cost = distanceTriangulate(loc_to_check,goal) * 10

        neighbours.append(Node(loc_to_check, g_cost,h_cost))

    steps[len(steps) - 1].neighbours = neighbours[:]

    min_node : Node = None
    coming_from : Node = None

    for i in range(len(steps)):
        for j in range(len(steps[i].neighbours)):
            # If the neighbour is already visited
            if isNodeTraversed(steps[i].neighbours[j].location, steps) == True:
                continue
            
            # If its empty give it the first element
            if min_node == None:
                min_node = steps[i].neighbours[j]
                coming_from = steps[i]
                continue
            
            if steps[i].neighbours[j].f_cost < min_node.f_cost :
                min_node = steps[i].neighbours[j]
                coming_from = steps[i]
            elif steps[i].neighbours[j].f_cost == min_node.f_cost:
                if steps[i].neighbours[j].h_cost < min_node.h_cost:
                    min_node = steps[i].neighbours[j]
                    coming_from = steps[i]
    
    # If a min node exists (there should be)
    if min_node != None:
        min_node.coming_from = coming_from
        steps.append(min_node)

        return aStar(min_node.location, goal, steps, tiles, tiles_to_follow)
         
    
    print("A* Problem!")
    return None

''' 
def calculateDistance(curr : Coordinate, goal : Coordinate, steps : List[Coordinate], tiles : List[List[Tiles]], tiles_to_follow : List[Tiles]):
    # Copy the list
    steps = steps[:]

    # Check if its the goal
    if curr.X == goal.X and curr.Y == goal.Y:   
        # Add the current location to steps
        steps.append(curr)

        return steps

    # Skip if the current location is out of bounds or filtered out
    if isWithinBounds(curr, tiles) == False or shouldFollowTile(curr,tiles,tiles_to_follow) == False:
        return None
    
    # Check if the location is already been traversed
    for coord in steps:
        if curr.X == coord.X and curr.Y == coord.Y:
            return None

    # Add the current location to steps
    steps.append(curr)

    # Number of steps 
    distances : List[List[Coordinate]] = []

    # Check for all directions
    # If the direction is out of bounds it will return none
    for dir in Directions:
        dir : Coordinate = dir.value

        loc_to_check = Coordinate(curr.X + dir.X, curr.Y + dir.Y)
        
        distance = calculateDistance(loc_to_check,goal,steps,tiles,tiles_to_follow)    
        distances.append(distance)

    path_taken = None

    for dist in distances:
        if dist == None:
            continue

        if path_taken == None:
            path_taken = dist
            continue

        if len(dist) < len(path_taken):
            path_taken = dist
    
    return path_taken
'''