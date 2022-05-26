from game import *

class Level:
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
        for plane in Level_Plane.__subclasses__():
            self.all_plane_classes.append(plane)
        self.score = 0
        self.lost = False
        self.timer = 2  # timer to keep track of planes spawning
        self.timeLimit = 2  # time limit between planes spawning
        self.current_level = 1  # current level of the game view
        self.limit = 4  # limit of planes to spawn
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        mixer.init()
        mixer.music.load('Assets/sounds/music_loop.wav')
        mixer.music.set_volume(0.05)
        mixer.music.play(-1)

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

        if self.planes:
            for plane in self.planes:
                # if the level is 3, change the color of the plane image to red
                if plane.level == 3:
                    plane.fill(pygame.Color(255, 0, 0, 100))
                elif plane.level == 2:
                    # use the pixel array of the plane_img to change the color of the plane image to green
                    plane.fill(pygame.Color(0, 0, 255, 100))
                elif plane.level == 1:
                    # use the pixel array of the plane_img to change the color of the plane image
                    plane.fill(pygame.Color(0, 255, 0, 100))

                plane.draw(self)
                self.screen.blit(self.font.render(str(plane.level), 1, (255, 255, 255)), (plane.x, plane.y + 50))


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
                    if plane.level == other_plane.level:
                        self.handle_plane_collisions(plane, other_plane)

            elif plane.level == self.current_level:
                plane.handle_runway(self)


    def handle_plane_collisions(self, plane, other_plane):
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
                    plane_pos = (
                    plane.x - plane.plane_img.get_rect().width / 2, plane.y - plane.plane_img.get_rect().height / 2)
                    other_pos = (other_plane.x - other_plane.plane_img.get_rect().width / 2,
                                 other_plane.y - other_plane.plane_img.get_rect().height / 2)
                    midpoint = (((plane_pos[0] + other_pos[0] - plane_warning.get_rect().width / 2)) / 2 ,
                                ((plane_pos[1] + other_pos[1] - plane_warning.get_rect().height / 2)) / 2 )
                    self.screen.blit(plane_warning, (midpoint[0], midpoint[1]))

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
                        if pygame.mouse.get_pressed()[0] and plane.plane_img.get_rect(center=(plane.x, plane.y)).collidepoint(event.pos):
                            self.cursor.holding = True
                            plane.selected = True
                            plane.new_select = True
                            plane.interacted = True

            # check if the right mouse button is clicked, check if a plane has been clicked by the right mouse button
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                for plane in self.planes:
                   if plane.plane_img.get_rect(center=(plane.x, plane.y)).collidepoint(event.pos):
                       if plane.level > 1:
                        plane.level -= 1
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
            # add a plane to the game at a random location every 20 seconds if there are less than 10 planes
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

# load the image of the a310 plane and set it to a variable and resize the image to half the size
BIG_PLANE = pygame.image.load('Assets/a310.png')
SMALL_PLANE = pygame.transform.scale(BIG_PLANE, (int(BIG_PLANE.get_width() / 1.5), int(BIG_PLANE.get_height() / 1.5)))
TINY_PLANE = pygame.transform.scale(pygame.image.load('Assets/cessna.png'),
                                    (int(BIG_PLANE.get_width() / 2), int(BIG_PLANE.get_height() / 2)))
FAST_PLANE = pygame.image.load('Assets/b17.png')
SEA_PLANE = pygame.image.load('Assets/sea_plane.png')
HELI_PLANE = pygame.image.load('Assets/heli1.png')
HELI_PLANE2 = pygame.image.load('Assets/heli2.png')
HELI_PLANE3 = pygame.image.load('Assets/heli3.png')

UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)

class Level_Plane():
    def __init__(self, x, y, direction, level):
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
        self.first_collided = False
        self.selected = False
        self.new_select = False
        self.inside = False
        self.level = level
        self.movements = []
        self.movements_length = len(self.movements)
        self.interacted = False
        self.length_of_movements = 0

    def fill(self, color):
        """Fill all pixels of the surface with color, preserve transparency."""
        image = self.plane_img.copy()
        image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        image.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
        self.plane_img = image

    def draw(self, game):
        '''
        Draw the plane using an offset to the center of the plane
        :param win: the window to draw the plane on
        :return:
        '''
        x_offset = self.x - self.plane_img.get_rect().width / 2
        y_offset = self.y - self.plane_img.get_rect().height / 2

        # for each movement in the list, draw a line from the last coordinate to the current one
        if self.movements and game.playing:
            for i in range(len(self.movements)):
                if i == 0:
                    continue
                # only draw every other line
                pygame.draw.line(game.screen, (80, 80, 80), (self.movements[i - 1][0], self.movements[i - 1][1]),
                                 (self.movements[i][0], self.movements[i][1]), 3)

        if self.movements and game.playing:
            # draw a dot at the last coordinate in the list
            pygame.draw.circle(game.screen, (80, 80, 80), (self.movements[-1][0], self.movements[-1][1]), 6)

        # draw the plane
        game.screen.blit(self.plane_img, (x_offset, y_offset))

    # move the plane in the direction of the direction vector
    def move(self, cursor):
        '''
        Change the x and y coordinates of the plane based on the direction vector
        param cursor: the cursor
        return:
        '''
        if self.movements:
            self.track_movements(cursor)
            return
        self.rect = pygame.rect.Rect(self.x - self.plane_img.get_rect().width / 2,
                                     self.y - self.plane_img.get_rect().height / 2, self.plane_img.get_rect().width,
                                     self.plane_img.get_rect().height)
        self.smooth_angle()
        self.plane_image_check()
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.x += self.vel * self.direction[0]
        self.y += self.vel * self.direction[1]

    def smooth_angle(self):
        """
        This will smooth the angle of the plane so that it doesn't jerk when it moves
        This is done by calculating what the new angle should be and then calculating,
         the difference between the current angle and the new angle
        Then the angle is set to the new angle plus the difference
        :return:
        """
        new_angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        # smooth angles out
        if abs(new_angle - self.angle) > 1:
            if new_angle > self.angle:
                difference = new_angle - self.angle
                if difference > 180:
                    difference -= 360
                elif difference < -180:
                    difference += 360
                self.angle += difference / 10
            elif new_angle < self.angle:
                difference = self.angle - new_angle
                if difference > 180:
                    difference -= 360
                elif difference < -180:
                    difference += 360
                self.angle -= difference / 10
            elif new_angle == self.angle:
                self.angle = new_angle
        else:
            self.angle = new_angle


    def track_movements(self, cursor):
        '''
        This will track the movements array and change the vector of the plane
        depending on where the next movement is
        :param cursor:
        :return:
        '''
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

        new_angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi

        # smooth angles out
        self.smooth_angle()
        self.plane_image_check()
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)

    def wall_collide(self, mask, x=0, y=0):
        '''
        Manages the plane collision with the walls
        :param mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi

    def plane_collide(self, other_plane):
        '''
        Manages the plane collisions with other planes
        using the offset of both planes
        :param other_plane:
        :return:
        '''
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
        '''
        Manages the collisions between the plane and the runway
        :param runway_mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = runway_mask.overlap(plane_mask, offset)
        return poi

    def plane_image_check(self):
        '''
        Sets the plane image using the subclasses
        :return:
        '''
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Level_Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.default_img

    def handle_runway(self, game):
        for plane in Level_Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                if self.runway_collide(self.runway_mask, 0, 0) and self.interacted is not False:
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
        self.interacted = False

# create a child class of the plane class called small plane
class SmallPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SMALL_PLANE, self.angle)
        self.default_img = SMALL_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.9
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


# create a child class of the plane class called big plane
class BigPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(BIG_PLANE, self.angle)
        self.default_img = BIG_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.0
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class FastPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(FAST_PLANE, self.angle)
        self.default_img = FAST_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.2
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class TinyPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(TINY_PLANE, self.angle)
        self.default_img = TINY_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.8
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class SeaPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SEA_PLANE, self.angle)
        self.default_img = SEA_PLANE
        self.runway_mask = SEA_MASK
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.6
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class HeliPlane(Level_Plane):
    def __init__(self, x, y, direction, level):
        super().__init__(x, y, direction, level)
        self.plane_id = self.__class__.__name__
        self.animations = [HELI_PLANE, HELI_PLANE2, HELI_PLANE3]
        self.animation_frame = 0
        self.plane_img = pygame.transform.rotate(self.animations[self.animation_frame], self.angle)
        self.default_img = HELI_PLANE
        self.runway_mask = HELI_MASK
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.4
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

    def plane_image_check(self):
        '''
        Sets the plane image using the subclasses
        :return:
        '''
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Level_Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.animations[self.animation_frame]
                self.animation_frame += 1
                if self.animation_frame == len(self.animations):
                    self.animation_frame = 0

    def refract(self, collide_point):
        if not self.inside:
            return
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 3
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 3
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 3
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 3

        self.plane_image_check()
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.interacted = False

    def wall_collide(self, mask, x=0, y=0):
        '''
        Manages the plane collision with the walls
        :param mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi