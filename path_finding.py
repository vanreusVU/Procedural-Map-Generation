# Default Modules
import math
from typing import List

# Custom Modules
from dungeon_tiles import Tiles
from utilities import Coordinate, Directions, isWithinBounds

class Node():
    ''' A class that represents the nodes in a tile map to be used for A* pathfinding algorithm '''

    def __init__(self, location : Coordinate, g_cost : float = 0, h_cost : float = 0, e_cost : float = 0):
        '''
        :param location: location of the node
        :type location: Coordinate
        :param g_cost: distance from the starting node, defaults to 0
        :type g_cost: float, optional
        :param h_cost: distance from the end node, defaults to 0
        :type h_cost: float, optional
        :param e_cost: extra costs, defaults to 0
        :type e_cost: float, optional
        '''     

        # Coordinates of the current node
        self.location = location
        
        # Cost of the current node
        self.g_cost : float = g_cost 
        self.h_cost : float = h_cost

        # For extra costs to add to the node
        self.e_cost : float = e_cost

        # Node that leads to this node
        self.coming_from : Node = None

        # Final cost    
        self.f_cost : float = self.g_cost + self.h_cost + self.e_cost
    
        # Costs of the neighbours
        self.neighbours : List[Node] = None
        pass

def distanceTriangulate(location : Coordinate, goal : Coordinate) -> int:
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

    
    :param location: from location
    :type location: Coordinate
    :param goal: to location
    :type goal: Coordinate
    :return: returns distance in int
    :rtype: float
    '''  

    return abs(location.X - goal.X) + abs(location.Y - goal.Y)

def distancePythagorean(location : Coordinate, goal : Coordinate) -> float:
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

    :param location: from location
    :type location: Coordinate
    :param goal: to location
    :type goal: Coordinate
    :return: returns distance in float
    :rtype: float
    '''    


    x = abs(location.X - goal.X)
    y = abs(location.Y - goal.Y)

    return math.sqrt(math.pow(x,2) + math.pow(y,2))
    
def isNodeTraversed(location : Coordinate, steps : List[Node]) -> bool:
    '''
    Check if the location is already been traversed

    :param location: location to search in steps
    :type location: Coordinate
    :param steps: steps taken
    :type steps: List[Node]
    :return: true if the location is already been traversed
    :rtype: bool
    '''    
    
    for node in steps:
        if location == node.location:
            return True

    return False

def aStar(curr : Coordinate, goal : Coordinate, steps : List[Node], tiles : List[List[Tiles]]) -> List[Coordinate]:
    '''
    Gets the shorthest path between curr and goal by using A* Pathfinding algorithm.
    https://en.wikipedia.org/wiki/A*_search_algorithm

    :param curr: current location
    :type curr: Coordinate
    :param goal: target location
    :type goal: Coordinate
    :param steps: current traveled locations
    :type steps: List[Node]
    :param tiles: tiles(2D matrix) to navigate in
    :type tiles: List[List[Tiles]]
    :param rooms: Start and end room
    :type steps: List[Room]
    :return: the shorthest path from inital curr to goal
    :rtype: List[Coordinate]
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
        dir : Coordinate = dir.value

        loc_to_check = Coordinate(curr.X + dir.X, curr.Y + dir.Y)

        # Skip if the current location is out of bounds or is a blocking tile
        if isWithinBounds(loc_to_check, tiles) == False or (tiles[loc_to_check.Y][loc_to_check.X] in Tiles.BLOCKING_TILES):
            continue 
        
        # Check if the location is already been traversed
        if isNodeTraversed(loc_to_check,steps) == True:
            continue

        # distance from starting node
        g_cost = distanceTriangulate(loc_to_check,steps[0].location) * 10
        # distance from the end node
        h_cost = distanceTriangulate(loc_to_check,goal) * 10

        # EXTRA GUIDANCE
        e_cost = 0

        # Follow the soft_ignore_walls
        if tiles[loc_to_check.Y][loc_to_check.X] == Tiles.SOFT_IGNORE_WALL:
            e_cost -= (g_cost + h_cost) / 2
        
        # Follow the already existing paths (other corridors)
        if tiles[loc_to_check.Y][loc_to_check.X] == Tiles.PATH: 
            e_cost -= (g_cost + h_cost) / 2

        neighbours.append(Node(loc_to_check, g_cost,h_cost,e_cost))

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

        return aStar(min_node.location, goal, steps, tiles)
         
    
    print("A* Problem!")
    return []
    