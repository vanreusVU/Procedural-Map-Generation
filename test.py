from triangulation import Edge
from utilities import Coordinate

c = [Edge(Coordinate(5,2), Coordinate(5,3)),Edge(Coordinate(5,5), Coordinate(5,2))]
a = Edge(Coordinate(5,2), Coordinate(5,2))
b = Edge(Coordinate(5,2), Coordinate(5,2))

print(a in c)