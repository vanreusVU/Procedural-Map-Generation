'''first_pos = (3,2)
second_pos = (7,7)

width = abs(first_pos[0] - second_pos[0]) + 1
height = abs(first_pos[1] - second_pos[1]) + 1

print("width: ", width, " height: ", height)

tiles = [["x"] * width for _ in range(height)]

print(len(tiles), " " , print(len(tiles[0])))'''

room_layout = '''\
    x x x x
    x o o D
    x o o x x
    x o o o x
    x x x x x
'''.splitlines()

room_layout = [[i for i in line.split()] for line in room_layout]
for y, row in enumerate(room_layout):
    print("x1:", 0, "x2:", len(row) - 1, end = " <-> ")
    print("y1:", 0, "y2:", len(room_layout) - 1)