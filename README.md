# Procedural Map Generation

In computing, procedural generation is a method of creating data algorithmically as opposed to manually, typically through a combination of human-generated assets and algorithms coupled with computer-generated randomness and processing power. In computer graphics, it is commonly used to create textures and 3D models. In video games, it is used to automatically create large amounts of content in a game. Depending on the implementation, the advantages of procedural generation can include smaller file sizes, larger amounts of content, and randomness for less predictable gameplay. Procedural generation is a branch of media synthesis.

Procedural Map Generation algorithms for rogue-like games. I will try to implement all of the algorithms below.  

**Algorithms in this repo:**
- [x] Simpe Room Placement
- [x] Binary Space Partitioning(BSP) Room Placement
- [ ] Voranoi Diagrams
- [ ] Perlin/Simplex Noise
- [ ] Cellular Automata
- [x] Delaunay Triangulation
- [x] A* pathfinding
- [ ] Drunkard's Walk
- [ ] Diffusion Limited Aggregation

**For optimization:**
- [ ] Dijkstra Maps
- [ ] Hot Path  

## Experiment 1: Simpe Room Placement, A* pathfinding, Delaunay Triangulation

<img src="https://i.imgur.com/UkuRm6P.gif" width="480" height="480" />

As you can guess from the name this is the simplest way to place rooms. What you want to do is before placing the room check the location that the room will cover. If it's overlapping with any other object, choose another location and check again. Do this over and over again until you can find a suitable location.

```python
MAX_NUMBER_OF_TRIES = 50

def placeRoom(room):
  # To avoid an endless loop we need to limit the amount of searches
  for MAX_NUMBER_OF_TRIES:
    room_location = random location on the map
    if room is placeable at room_location:
      Add room to the map
      break
```

### Linking the Rooms
Now that we have the rooms placed we need to connect them. There are multiple ways of doing this such as, using proximity to link rooms. In this example, I used [delaunay triangulation](https://github.com/vanreusVU/Delaunay-Triangulation) in order to connect each room together. Afterward, I used prim's algorithm to find the minimum spanning tree amongst the connections. [Prim's Algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm) is used to find the minimum spanning tree from a graph. Prim's algorithm finds the subset of edges that includes every vertex of the graph such that the sum of the weights of the edges can be minimized. To add some variety to the dungeons I made some adjustments in the algorithm to allow loops in some cases.

```python
# If both sides are visited the path will be counted if random number is less than chance_of_loop
# With this we can add some variaty to the dungeon by adding loops
if any([vert1_in, vert2_in]) and is_loop_allowed:
    if not edge in self.paths:
        # Add the current edge to the potential_paths
        potential_paths.append(edge)
```

After this, you check the resulted tree for big loops to avoid non-linear maps. With the list of connections, we can add doors to the rooms such that each room will have as many rooms as the number of connections the room has.

### Creating the doors
Creating the doors was more of a problem than I imagined. Most of the approach that I saw online was to create corridors from the center of one room to the others and turn the contact point into a door. The problem I had with this approach was no uniqueness in the placement of the doors. All of the doors were in the center of the room. To fix this instead of creating corridors from room center to room center, I created corridors from door to door. What I mean by that is, whenever, I wanted to connect two rooms, I've created a randomly generated door on both of the rooms and connected them instead. For generating random doors, I've followed a simple algorithm. 

Door placement:
- Choose a random wall tile location
- Check if it's a corner piece. (We don't want to place doors on the corner pieces)
- Check the tiles around the location to see if the door is blocked
- If everything is fine place the door. Else, choose a new location

```python
vertical_sum = 0
horizontal_sum = 0

for i in range(-1,2):
    loc_to_check = Coordinate(location.X + i, location.Y + i)

    # Ignore the center part
    if loc_to_check.X == location.X and loc_to_check.Y == location.Y:
        continue

    # Check on y axis
    if loc_to_check.Y >= 0 and loc_to_check.Y < len(tiles): 
        if tiles[loc_to_check.Y][location.X] in blocks_to_check:
            vertical_sum += 1
    elif out_of_bounds_check:
        vertical_sum += 1

    # Check on x axis
    if loc_to_check.X >= 0 and loc_to_check.X < len(tiles[0]):
        if tiles[location.Y][loc_to_check.X] in blocks_to_check:
            horizontal_sum += 1
    elif out_of_bounds_check:
        horizontal_sum += 1

return Coordinate(horizontal_sum, vertical_sum)
```

### Placing Corridors
Placing the corridors was another tricky part that I needed to figure out. The most common approach was to create L-shaped corridors between points. However, it was not possible for me to use it because of the random door placing that I've been using. Instead, I went with [the A* pathfinding algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) to find the best connection between the rooms. A* is an informed search algorithm, or a best-first search, meaning that it is formulated in terms of weighted graphs: starting from a specific starting node of a graph, it aims to find a path to the given goal node having the smallest cost (least distance traveled, shortest time, etc.). It does this by maintaining a tree of paths originating at the start node and extending those paths one edge at a time until its termination criterion is satisfied. With A* I was able to create corridors that avoid other objects by maneuvering around them. However, there was one problem with A* which is using the Pythagorean theorem for calculating the distance. This resulted in corridors that goes diagonal. My solution was instead of getting the hypotenuse of the triangle I took the height and width of it. In the end i'm happy with A* apart from the time complexity side of the things. Depanding on the map size the algorithm might be too costly to consider.

```python
abs(location.X - goal.X) + abs(location.Y - goal.Y)
```

## Experiment 2: Binary Space Partitioning, A* pathfinding (not avoiding), Delaunay Triangulation

<img src="https://i.imgur.com/yBLWnF1.gif" width="480" height="480" />

Binary Space Partitioning (BSP) is a method for space partitioning which recursively subdivides a area into two sets by using smaller areas as partitions. This process of subdividing gives rise to a representation of objects within the space in the form of a tree data structure known as a BSP tree.

```python
def binarySpacePartitioning(self, area : SquareArea):
        '''
        Is a method for recursively subdividing a space into two convex sets by using hyperplanes as partitions.

        :param area: Area to devide
        :type area: SquareArea
        '''        

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
```
