import pygame
from settings import *
import plane as pl
from pygame import mixer
import random
import sys

# Creation of landing pad masks
UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)
# loads the wall and menu bg
WALL = pygame.image.load('assets/wall.png')


class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()
        self.playing = True
        self.cursor = Cursor()
        # create a self.screen
        self.length, self.height = 1280, 720
        self.screen = pygame.display.set_mode((1280, 720))
        self.background = pygame.image.load('assets/hawaii.png')
        pygame.display.set_caption("ATC Game")
        self.font = pygame.font.SysFont("arial", 20)
        self.wall = self.screen.blit(WALL, (0, 0))
        self.wallMask = pygame.mask.from_surface(WALL)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.planes = []
        self.all_plane_classes = []
        self.planes_on_runway = []
        for plane in pl.Plane.__subclasses__():
            self.all_plane_classes.append(plane)
        self.score = 0
        self.lost = False
        self.timer = 2  # timer to keep track of planes spawning
        self.timeLimit = 2  # time limit between planes spawning
        self.current_level = 1  # current level of the game view
        self.limit = 4  # limit of planes to spawn
        self.music_toggled = True
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        mixer.init()
        mixer.music.load('Assets/sounds/music_loop.wav')
        mixer.music.set_volume(0.3)
        mixer.music.play(-1)

    def music_toggle(self):
        if self.music_toggled:
            self.music_toggled = False
            mixer.music.pause()
        else:
            self.music_toggled = True
            mixer.music.unpause()

    def increase_score(self):
        self.score += 1
        self.limit += 0.5

    # create a function to draw objects
    def draw_objects(self):
        # draw the self.background image
        self.screen.blit(pygame.transform.scale(self.background, (1280, 720)), (0, 0))
        # create a label for the score
        self.scoreLabel = self.font.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.screen.blit(self.scoreLabel, (630, 10))
        # create a label for the lost message
        self.lostLabel = self.font.render("You Lost", 1, (255, 255, 255))
        # draw all the planes
        # check if the planes list is empty
        if self.planes_on_runway:
            for plane in self.planes_on_runway:
                alpha = plane.draw_runway(self)
                if alpha <= 0:
                    self.planes_on_runway.remove(plane)
        if self.planes:
            for plane in self.planes:
                plane.draw(self)

    def add_planes(self):
        if len(self.planes) < self.limit:
            # The below variables are to generate the x and y locations of the planes at each side
            randomspawnabove = (random.randint(0, 1280), random.randint(-200, -50))
            randomspawnbelow = (random.randint(0, 1280), (random.randint(720, 900)))
            randomspawnleft = (random.randint(-200, -50), random.randint(0, 720))
            randomspawnright = (random.randint(1350, 1500), random.randint(0, 720))
            x, y = random.choice([randomspawnleft, randomspawnright, randomspawnabove, randomspawnbelow])
            # choose a random coordinate on the game board
            direction_x_coord = random.randint(100, 1180)
            direction_y_coord = random.randint(100, 620)
            # create a vector between the plane and the coordinate
            vector_x = direction_x_coord - x
            vector_y = direction_y_coord - y
            vector = pygame.Vector2(vector_x, vector_y)
            vector = pygame.Vector2.normalize(vector)
            level = random.randint(1, 3)
            # loop through each subclass of Plane
            random_plane = random.choice(self.all_plane_classes)
            random_plane = random_plane(x, y, vector, level)
            self.planes.append(random_plane)

    def update_planes(self):
        for plane in self.planes:
            plane.move(self.cursor)

    def remove_plane(self, plane):
        self.planes_on_runway.append(plane)
        self.planes.remove(plane)
        return

    def handle_collisions(self):
        # for each plane in the planes list
        for plane in self.planes:
            if not plane.inside:
                # keep an eye on when the plane arrives inside the self.screen
                if plane.wall_collide(self.wallMask) is not None and plane.first_collided is False:
                    plane.first_collided = True
                elif plane.first_collided:
                    if plane.wall_collide(self.wallMask) is None:
                        plane.inside = True

                # handle collisions when the is outside the map
                for other_plane in self.planes:
                    if plane != other_plane and not other_plane.inside:
                        if plane.plane_collide(other_plane) is not None:
                            # remove the newer plane
                            self.planes.remove(plane)
                            print("Prevented OOB Overlap")

            if plane.inside:
                # handle collisions with the wall
                collide_point = plane.wall_collide(self.wallMask)
                if collide_point is not None:
                    plane.movements = []
                    plane.refract(collide_point)
                # for each plane, check if it collided any other planes and remove them

                # for each plane, check if it collided any other planes and remove them
                for other_plane in self.planes:
                    if plane != other_plane:
                        if plane.plane_collide(other_plane) is not None:
                            # draw the explosion
                            x = other_plane.x
                            y = other_plane.y
                            offset = (
                                ((plane.x - plane.plane_img.get_rect().width / 2) - (
                                        x - other_plane.plane_img.get_rect().width / 2)),
                                ((plane.y - plane.plane_img.get_rect().height / 2) - (
                                        y - other_plane.plane_img.get_rect().height / 2)))
                            # blit the explosion image to the screen
                            self.lose_game()
                            if not self.playing:
                                plane_warning = pygame.image.load('Assets/planeWarning.png')
                                plane_pos = (plane.x - plane.plane_img.get_rect().width / 2,
                                             plane.y - plane.plane_img.get_rect().height / 2)
                                other_pos = (other_plane.x - other_plane.plane_img.get_rect().width / 2,
                                             other_plane.y - other_plane.plane_img.get_rect().height / 2)
                                midpoint = (((plane_pos[0] + other_pos[0] - plane_warning.get_rect().width / 2)) / 2,
                                            ((plane_pos[1] + other_pos[1] - plane_warning.get_rect().height / 2)) / 2)
                                self.screen.blit(plane_warning, (midpoint[0], midpoint[1]))

            # depending on the plane type, check if it collided with the appropriate runway
            plane.handle_runway(self)

    def lose_game(self):
        self.lost = True
        self.playing = False
        mixer.music.stop()
        mixer.music.load('Assets/sounds/collision.wav')
        mixer.music.set_volume(0.2)
        mixer.music.play(1)
        return

    def event_loop(self):
        for event in pygame.event.get():
            # check if the user wants to quit
            if event.type == pygame.QUIT:
                self.playing = False
                sys.exit()
                # check if mouse is clicking on a plane
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.cursor.holding:
                    for plane in self.planes:
                        if plane.plane_img.get_rect(center=(plane.x, plane.y)).collidepoint(event.pos):
                            self.cursor.holding = True
                            plane.selected = True
                            plane.new_select = True
                            plane.interacted = True

            if event.type == pygame.MOUSEBUTTONUP:
                for plane in self.planes:
                    if self.cursor.holding:
                        if plane.selected:
                            self.cursor.holding = False
                            plane.selected = False
                            plane.new_select = False
                self.cursor.holding = False

            if event.type == pygame.MOUSEMOTION:
                if self.cursor.holding:
                    for plane in self.planes:
                        if plane.selected:
                            self.cursor.set_path(True, plane)
            elif event.type == pygame.USEREVENT:
                if self.timer < self.timeLimit:
                    self.timer += 1
                elif self.timer == self.timeLimit:
                    self.timer = 0
                    self.add_planes()

    def game_loop(self):
        while self.playing:
            self.clock.tick(self.fps)
            self.draw_objects()  # draws all objects
            self.handle_collisions()
            self.event_loop()  # handles events
            self.update_planes()  # updates planes
            pygame.display.update()
        if not self.playing:
            self.draw_objects()
            self.handle_collisions()
            pygame.display.update()
            pygame.time.wait(3000)
        return

    def reset(self):
        self.__init__()