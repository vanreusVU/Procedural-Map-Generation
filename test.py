from utilities import Coordinate


a = [0,0,0]
b = [1,1,1]
c = [[0,0,0],[1,1,1]]
for i in range(len(c)):
    c[i] = c[i] + a

print(c)