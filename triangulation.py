from typing import List, Tuple
from utilities import Coordinate, MinMax


class Edge():
    ''' An edge consisting of the verticies '''
    def __init__(self, point1 : Coordinate, point2 : Coordinate) -> None:
        self.p1 = point1
        self.p2 = point2

    def __eq__(self, __o: object) -> bool:
        ''' Equality checks are based on the P1 and P2 values rather than instances'''
        if isinstance(__o, Edge):
            if isinstance(__o, list):
                __o = __o[0]
            return __o.p1 == self.p1 and __o.p2 == self.p2
        else:
            return super(Edge, self).__eq__(__o)

    def __ne__(self, __o: object) -> bool:
        ''' Equality checks are based on the P1 and P2 values rather than instances'''
        if isinstance(__o, Edge):
            if isinstance(__o, list):
                __o = __o[0]
            return __o.p1 != self.p1 or __o.p2 != self.p2
        else:
            return super(Edge, self).__ne__(__o)

class Triangle():
    ''' Triangle object to be used for triangulation '''
    def __init__(self, triangle_verticies, triangle_neighbors = []) -> None:
        self.verticies : List[Coordinate] = self.orderVerticies(triangle_verticies)
        self.edges : List[Edge] = self.getEdges()
        self.neighbors : List[Triangle] = triangle_neighbors
    
    # TODO: Fix this to Counter clockwise order with the top left one being the first
    def orderVerticies(self,verticies : List[Coordinate]) -> List[Coordinate]:
        ''' Orders the verticies in a way that first vertex is the bottom one, second one is clockwise from vertex 1 '''
    
        # [0] is lowest Y
        # [1] is lowest X
        # [2] is remaning 
        ordered_vert : List[Coordinate] = [None,None,None]

        if len(verticies) < 1 and len(verticies) > 3:
            print("Error with given verticies. There has to be min 2 max 3 verticies in the given list")
            return []

        for i in range(len(verticies)):
            for j in range(len(verticies)):
                if verticies[j].Y < verticies[0].Y:
                    temp_vert = verticies[0]
                    verticies[0] = verticies[j]
                    verticies[j] = temp_vert
                elif verticies[j].X < verticies[1].X:
                    temp_vert = verticies[1]
                    verticies[1] = verticies[j]
                    verticies[j] = temp_vert
        
        # If only 2 verticies are given leave the last one as None
        ordered_vert[0:len(verticies)] = verticies[:]

        return ordered_vert

    def getEdges(self) -> List[Edge]:
        return []

    def __str__(self) -> str:
        return f"Triangle: \nP1: {self.verticies[0]}\nP2: {self.verticies[1]}\nP3: {self.verticies[2]}"

def determinant(matrix):
    '''Return the determinant of the given 2d matrix'''
    
    determinants = []

    # Final stage where you return the determinant of the given 2x2
    if len(matrix) == 2:
        return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])

    # Go thourgh the first row and take their detarminants
    for i in range(len(matrix)):
        # Quick list comprehension to remove the needed rows and columns
        new_matrix = [[matrix[y][x] for x in range(len(matrix[y])) if x != i] for y in range(len(matrix)) if y != 0]
        new_determinant = determinant(new_matrix)

        # Tuple [0] = main element
        # Tuple [1] = resulting determinant of that element
        determinants.append((matrix[0][i] , new_determinant))

    if len(determinants) == 0:
        print("ERROR in matrix")
        return -1

    total = determinants[0][0] * determinants[0][1]
    for i in range(1, len(determinants)):
        if i % 2 != 0:
            total -= determinants[i][0] * determinants[i][1]
        else:
            total += determinants[i][0] * determinants[i][1] 

    return total

def isWithinCircumcircle(point : Coordinate, triangle : Triangle):
    '''
    Returns true if the given point is within the circumcircle of the given triangle.
    IMPORTANT: Give the triangle points in counterclockwise order
    '''
    
    determ_matrix = []
    points_to_work = [point]
    points_to_work[:0] = triangle.verticies[:]

    for tri_point in points_to_work:
        x = tri_point.X
        y = tri_point.Y

        sum_squared = pow(x,2) + pow(y,2)

        determ_matrix.append([x,y,sum_squared,1])

    return determinant(determ_matrix) > 0


def getEdgePoints(points : List[Coordinate]) -> MinMax(Coordinate, Coordinate):
    ''' 
    Finds the Xmin, Xmax, Ymin, Ymax coordinates of the given points.
    '''
    
    if len(points) <= 0:
        print("ERROR: Empty list")
        return None


    place_holder = points[0]
    max : Coordinate = Coordinate(place_holder.X, place_holder.Y)
    min : Coordinate = Coordinate(place_holder.X, place_holder.Y)

    for point in points:
        if point.X > max.X:
            max.X = point.X
        
        if point.Y > max.Y:
            max.Y = point.Y
        
        if point.X < min.X:
            min.X = point.X
        
        if point.Y < min.Y:
            min.Y = point.Y

    return MinMax(min,max)

# Could implement a better super triangle method. Driving from convex hull maybe?
def getSuperTriangle(edgePoints : MinMax) -> Triangle:
    ''' Returns a triangle that covers the given edge points '''
    safetey_length = 30
    # Center the point by getting the min point of min and max X, then go up from the max y to get to a safe distance
    p1 : Coordinate = Coordinate(edgePoints.MIN.X + (edgePoints.MAX.X - edgePoints.MIN.X) / 2, edgePoints.MIN.Y - safetey_length)
    
    # Go to the corners safe distance
    p2 : Coordinate = Coordinate(edgePoints.MAX.X + safetey_length, edgePoints.MAX.Y + safetey_length)
    p3 : Coordinate = Coordinate(edgePoints.MIN.X - safetey_length, edgePoints.MAX.Y + safetey_length)

    return Triangle([p1,p2,p3])

def bowyerWatson(points : List[Coordinate]) -> List[Triangle]:
    ''' Creates delaunay triangulation using bowyer and watson algorithm '''

    # points is a list of coordinates defining the points to be triangulated
    triangulation : List[Triangle] = []
    
    # Create a super triangle that contains all of the points within it
    super_triangle = getSuperTriangle(getEdgePoints(points))

    # Add the super triangle to the triangulation list
    triangulation.append(super_triangle)

    for point in points:
        bad_triangles : List[Triangle] = []

        # Check for triangles that doesn't follow the circumcirlce rule after insterting the point
        for triangle in triangulation:
            if isWithinCircumcircle(point, triangle):
                bad_triangles.append(triangle)

        polygon : List[Coordinate] = []

        # Find the boundary of the polygonal hole
        for triangle in bad_triangles:
            for edge in triangle.edges:
                pass

    return triangulation