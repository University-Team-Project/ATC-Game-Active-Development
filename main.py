import pygame
from pygame import *
import sys
from settings import *
import random
import time
import plane as pl
from Button import *

# loads the bg assets from the assets folders
BACKGROUND = pygame.image.load('assets/hawaii.png')
# Creation of landing pad masks
UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)
# loads the wall and menu bg
WALL = pygame.image.load('assets/wall.png')
MENUBACKGROUND = pygame.image.load('Main Menu Assets/Group.png')
SCREEN = pygame.display.set_mode((1280, 720))

# create a game class to create the game
class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()
        self.playing = True
        self.menu = True
        self.cursor = Cursor()
        # create a screen
        self.length, self.height = 1280, 720
        self.screen = pygame.display.set_mode((1280, 720))
        # set the title of the screen
        pygame.display.set_caption("ATC Game")
        # create a font for the text that uses arial and is 20 pixels
        self.font = pygame.font.SysFont("arial", 20)
        # create a border round the edge of the screen
        self.wall = self.screen.blit(WALL, (0, 0))
        self.wallMask = pygame.mask.from_surface(WALL)
        # create a clock
        self.clock = pygame.time.Clock()
        # set the fps
        self.fps = 60
        self.planes = []
        self.all_plane_classes = []
        for plane in pl.Plane.__subclasses__():
            self.all_plane_classes.append(plane)
        self.score = 0
        self.lost = False
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.timer = 3
        self.timeLimit = 3

        # set an integer to limit the number of planes
        self.limit = 3

    def increase_score(self):
        self.score += 1
        self.limit += 0.5

    # create a function to draw objects
    def draw_objects(self):
        # draw the background image
        self.screen.blit(pygame.transform.scale(BACKGROUND, (1280, 720)), (0, 0))
        # create a label for the score
        self.scoreLabel = self.font.render("Score: " + str(self.score), 1, (255, 255, 255))
        SCREEN.blit(self.scoreLabel, (630, 10))
        # create a label for the lost message
        self.lostLabel = self.font.render("You Lost", 1, (255, 255, 255))
        # draw all the planes
        # check if the planes list is empty

        if self.lost:
            # take user back to the main menu
            self.menu = True
            restart_game()
        else:
            if self.planes:
                for plane in self.planes:
                    plane.draw(self.screen)

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
            # loop through each subclass of Plane
            random_plane = random.choice(self.all_plane_classes)
            random_plane = random_plane(x, y, vector)
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
                # keep an eye on when the plane arrives inside the screen
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
                            self.planes.remove(plane)
                            self.planes.remove(other_plane)
                            self.lose_game()
                            print("Collision between [", plane.x, plane.y, "] and [", other_plane.x, other_plane.y, "]")
                            print("Collision between" + str(plane) + " and " + str(other_plane))
            # depending on the plane type, check if it collided with the appropriate runway
            plane.handle_runway(self)

    def lose_game(self):
        self.lost = True

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
                        x_offset = plane.x - plane.plane_img.get_rect().width / 2
                        y_offset = plane.y - plane.plane_img.get_rect().height / 2
                        if plane.plane_img.get_rect(topleft=(x_offset, y_offset)).collidepoint(event.pos):
                            self.cursor.holding = True
                            plane.selected = True
                            plane.new_select = True
                            print("plane selected")

            if event.type == pygame.MOUSEBUTTONUP:
                for plane in self.planes:
                    if self.cursor.holding:
                        if plane.selected:
                            self.cursor.holding = False
                            plane.selected = False
                            plane.new_select = False
                            print("Holding State: ", self.cursor.holding)
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


# Retrieve Custom font for main menu
def get_font(size):
    return pygame.font.Font("Main Menu Assets/font.ttf", size)


def how_to_play():
    while True:
        options_mouse_pos = pygame.mouse.get_pos()

        SCREEN.fill("white")

        how_to_play_text = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        how_to_play_rect = how_to_play_text.get_rect(center=(640, 260))
        SCREEN.blit(how_to_play_text, how_to_play_rect)

        how_to_play_back = Button(image=None, pos=(640, 460),
                                  text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        how_to_play_back.changeColor(options_mouse_pos)
        how_to_play_back.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if how_to_play_back.checkForInput(options_mouse_pos):
                    return

        pygame.display.update()

def main_menu():
    game = Game()
    while game.menu:
        game.clock.tick(game.fps)

        SCREEN.blit(BACKGROUND, (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("MAIN MENU", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(640, 100))

        play_button = Button(image=pygame.image.load("Main Menu Assets/Play Rect.png"), pos=(640, 250),
                             text_input="PLAY", font=get_font(64), base_color="#d7fcd4", hovering_color="White")
        how_to_play_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 400),
                                    text_input="TUTORIAL", font=get_font(64), base_color="#d7fcd4",
                                    hovering_color="White")
        quit_button = Button(image=pygame.image.load("Main Menu Assets/Quit Rect.png"), pos=(640, 550),
                             text_input="QUIT", font=get_font(64), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(menu_text, menu_rect)

        for button in [play_button, how_to_play_button, quit_button]:
            button.changeColor(menu_mouse_pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    game.menu = False
                    break
                elif how_to_play_button.checkForInput(menu_mouse_pos):
                    how_to_play()
                elif quit_button.checkForInput(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

    print("Reached")
    game.playing = True
    return game


def game_loop(game):
    # create a variable to keep track of the game l
    # create a loop to keep the game running
    while game.playing:
        game.clock.tick(game.fps)
        game.handle_collisions()
        game.draw_objects()  # draws all objects
        game.event_loop()  # handles events
        game.update_planes()  # updates planes
        pygame.display.update()
    # end_game(game)


def end_game(game):
    print("end screen")


def restart_game():
    game = main_menu()
    game_loop(game)


if __name__ == '__main__':
    restart_game()
