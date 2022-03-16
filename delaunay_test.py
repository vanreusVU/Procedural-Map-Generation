from random import randint
import sys
from typing import List
import pygame
from color_constants import Color
from triangulation import Triangle, bowyerWatson
from utilities import Coordinate, MinMax

PIXEL_SIZE = 30
SCREEN_WIDTH, SCREEN_HIGHT = 720, 720

NUM_POINTS = 6

MINMAX_X = MinMax(
    int(((SCREEN_WIDTH / PIXEL_SIZE) / 2) - ((SCREEN_WIDTH / PIXEL_SIZE) / 4)),
    int(((SCREEN_WIDTH / PIXEL_SIZE) / 2) + ((SCREEN_WIDTH / PIXEL_SIZE) / 4))
)

MINMAX_Y = MinMax(
    int(((SCREEN_HIGHT / PIXEL_SIZE) / 2) - ((SCREEN_HIGHT / PIXEL_SIZE) / 4)),
    int(((SCREEN_HIGHT / PIXEL_SIZE) / 2) + ((SCREEN_HIGHT / PIXEL_SIZE) / 4))
)

class DelaunayTest():

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))
        self.clock = pygame.time.Clock()

        self.triangles : List[Triangle] = []
        self.points : List[Coordinate] = []

        # Create points
        self.createRandomPoints()

        self.begin()
        

    def circle(self, pos : Coordinate, color : Color = Color.WHITE):
        pos = ((pos.X * PIXEL_SIZE) + PIXEL_SIZE/2 , (pos.Y * PIXEL_SIZE)+ PIXEL_SIZE/2)
        pygame.draw.circle(self.screen , color, pos, 10)

    def line(self, from_cord : Coordinate, to_cord : Coordinate, color : Color = Color.RED):
        from_cord = ((from_cord.X * PIXEL_SIZE) + PIXEL_SIZE/2 , (from_cord.Y * PIXEL_SIZE)+ PIXEL_SIZE/2)
        to_cord = ((to_cord.X * PIXEL_SIZE) + PIXEL_SIZE/2 , (to_cord.Y * PIXEL_SIZE)+ PIXEL_SIZE/2)

        pygame.draw.line(self.screen, color, from_cord, to_cord, 3)

    # Get Triangles based on the given algorithm
    def getTriangulation(self):
        self.triangles = bowyerWatson(self.points)

    def createRandomPoints(self):
        for _ in range(NUM_POINTS):
            x = randint(MINMAX_X.MIN, MINMAX_X.MAX)
            y = randint(MINMAX_Y.MIN, MINMAX_Y.MAX)

            point = Coordinate(x, y)

            if point in self.points:
                continue

            self.points.append(point)


    def draw(self):
        for point in self.points:
            self.circle(point)

        for triangle in self.triangles:
            for i in range(len(triangle.verticies)):
                if triangle.verticies[i] == None:
                    continue
                
                if i < len(triangle.verticies) - 1:
                    self.line(triangle.verticies[i], triangle.verticies[i + 1])
                else:
                    self.line(triangle.verticies[0], triangle.verticies[i])

        return

    def begin(self):
        while True:
            #CLOCK.tick(10)
            pygame.time.delay(100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(Color.BLACK)

            # Get triangles
            self.getTriangulation()

            # Call the drawing function
            self.draw()
            

            pygame.display.update()


if __name__ == "__main__":
    DelaunayTest()