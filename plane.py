import pygame
from pygame import *
import math

# load the image of the a310 plane and set it to a variable and resize the image to half the size
BIG_PLANE = pygame.image.load('Assets/a310.png')
SMALL_PLANE = pygame.transform.scale(BIG_PLANE, (int(BIG_PLANE.get_width() / 1.5), int(BIG_PLANE.get_height() / 1.5)))
TINY_PLANE = pygame.transform.scale(pygame.image.load('Assets/cessna.png'),
                                    (int(BIG_PLANE.get_width() / 2), int(BIG_PLANE.get_height() / 2)))
FAST_PLANE = pygame.image.load('Assets/b17.png')
SEA_PLANE = pygame.image.load('Assets/sea_plane.png')
HELI_PLANE = pygame.image.load('Assets/tokyo_heli1.png')

UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)

class Plane():
    def __init__(self, x, y, direction):
        super().__init__()
        self.plane_id = self.__class__.__name__
        self.x = x
        self.y = y
        self.vel = 0
        self.direction = direction
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(BIG_PLANE, self.angle)
        self.default_img = BIG_PLANE
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.runway_mask = LAND_MASK
        self.rect = pygame.rect.Rect(self.x - self.plane_img.get_rect().width / 2,
                                     self.y - self.plane_img.get_rect().height / 2, self.plane_img.get_rect().width,
                                     self.plane_img.get_rect().height)
        self.first_collided = False
        self.selected = False
        self.new_select = False
        self.inside = False
        self.movements = []


    def draw(self, win):
        x_offset = self.x - self.plane_img.get_rect().width / 2
        y_offset = self.y - self.plane_img.get_rect().height / 2

        # for each movement in the list, draw a line from the last coordinate to the current one
        for i in range(len(self.movements)):
            if i == 0:
                continue
            pygame.draw.line(win, (80, 80, 80), (self.movements[i - 1][0], self.movements[i - 1][1]),
                             (self.movements[i][0], self.movements[i][1]), 3)

        # draw the plane
        win.blit(self.plane_img, (x_offset, y_offset))

    # move the plane in the direction of the direction vector
    def move(self, cursor):
        if self.movements:
            self.track_movements(cursor)
            self.rect = pygame.rect.Rect(self.x - self.plane_img.get_rect().width / 2, self.y - self.plane_img.get_rect().height / 2, self.plane_img.get_rect().width, self.plane_img.get_rect().height)
            return
        self.rect = pygame.rect.Rect(self.x - self.plane_img.get_rect().width / 2,
                                     self.y - self.plane_img.get_rect().height / 2, self.plane_img.get_rect().width,
                                     self.plane_img.get_rect().height)
        self.x += self.vel * self.direction[0]
        self.y += self.vel * self.direction[1]

    def track_movements(self, cursor):
        # choose a random coordinate on the game board
        move = self.movements[0]
        # create a vector between the plane and the coordinate
        vector_x = move[0] - self.x
        vector_y = move[1] - self.y
        vector = pygame.Vector2(vector_x, vector_y)
        self.direction = pygame.Vector2.normalize(vector)
        self.x += self.vel * self.direction[0]
        self.y += self.vel * self.direction[1]
        if abs(self.x - move[0]) < 1 and abs(self.y - move[1]) < 1:
            self.movements.pop(0)
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_image_check()
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)


    def wall_collide(self, mask, x=0, y=0):
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi

    def plane_collide(self, other_plane):
        other_mask = other_plane.mask
        x = other_plane.x
        y = other_plane.y
        offset = (
            ((self.x - self.plane_img.get_rect().width / 2) - (x - other_plane.plane_img.get_rect().width / 2)) ,
            ((self.y - self.plane_img.get_rect().height / 2) - (y - other_plane.plane_img.get_rect().height / 2)) )
        poi = other_mask.overlap(self.mask, offset)
        # check if two masks overlap
        return poi

    def runway_collide(self, runway_mask, x, y):
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = runway_mask.overlap(plane_mask, offset)
        return poi

    def plane_image_check(self):
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.default_img

    def handle_runway(self, game):
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                if self.runway_collide(self.runway_mask, 0, 0):
                    game.planes.remove(self)
                    game.increase_score()

    def refract(self, collide_point):
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 10
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 10
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 10
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 10

        self.plane_image_check()
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)


# create a child class of the plane class called small plane
class SmallPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SMALL_PLANE, self.angle)
        self.default_img = SMALL_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.9
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


# create a child class of the plane class called big plane
class BigPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(BIG_PLANE, self.angle)
        self.default_img = BIG_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.0
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class FastPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(FAST_PLANE, self.angle)
        self.default_img = FAST_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.2
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class TinyPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(TINY_PLANE, self.angle)
        self.default_img = TINY_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.8
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class SeaPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SEA_PLANE, self.angle)
        self.default_img = SEA_PLANE
        self.runway_mask = SEA_MASK
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.6
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class HeliPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(HELI_PLANE, self.angle)
        self.default_img = HELI_PLANE
        self.runway_mask = HELI_MASK
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.4
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()
