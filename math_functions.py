from typing import List
from utilities import Coordinate


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

def isWithinCircumcircle(point : Coordinate, triangle : List[Coordinate]):
    '''
    Returns true if the given point is within the circumcircle of the given triangle.
    IMPORTANT: Give the triangle points in counterclockwise order
    '''

    # Add the point to the end of the list
    points = triangle.append(point)
    determ_matrix = []

    for tri_point in triangle:
        x = tri_point.X
        y = tri_point.Y

        sum_squared = pow(x,2) + pow(y,2)

        determ_matrix.append([x,y,sum_squared,1])

    return determinant(determ_matrix) > 0
