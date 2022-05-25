import sys

from pygame import mixer

from settings import *
import random
import plane as pl

# loads the bg assets from the assets folders

# Creation of landing pad masks
UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)
# loads the wall and menu bg
WALL = pygame.image.load('assets/wall.png')

class Menu:
    def __init__(self):
        pygame.init()
        self.menu = True
        self.cursor = Cursor()
        self.background = pygame.image.load('assets/hawaii.png')
        self.length, self.height = 1280, 720
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("ATC Game")
        self.clock = pygame.time.Clock()
        self.fps = 60
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    # Retrieve Custom font for main menu
    def get_font(self, size):
        return pygame.font.Font("Main Menu Assets/font.ttf", size)

    def how_to_play(self):
        how_to_play_text = self.get_font(45).render("This is the OPTIONS screen.", True, "Black")
        how_to_play_rect = how_to_play_text.get_rect(center=(640, 260))
        how_to_play_back = Button(image=None, pos=(640, 460),
                                  text_input="BACK", font=self.get_font(75), base_color="Black",
                                  hovering_color="Red")
        while True:
            options_mouse_pos = pygame.mouse.get_pos()
            self.screen.fill("white")
            self.screen.blit(how_to_play_text, how_to_play_rect)
            how_to_play_back.changeColor(options_mouse_pos)
            how_to_play_back.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if how_to_play_back.checkForInput(options_mouse_pos):
                        return

            pygame.display.update()

    def main_menu(self):
        game = Game()
        # generate random hex code
        hex_code = random.randint(0, 16777215)
        menu_text = self.get_font(100).render("MAIN MENU", True, '#00323d')
        menu_rect = menu_text.get_rect(center=(640, 100))

        play_button = Button(image=pygame.image.load("Main Menu Assets/Play Rect.png"), pos=(640, 250),
                             text_input="PLAY", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        how_to_play_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 400),
                                    text_input="TUTORIAL", font=self.get_font(64), base_color="#d7fcd4",
                                    hovering_color="Grey")
        quit_button = Button(image=pygame.image.load("Main Menu Assets/Quit Rect.png"), pos=(640, 550),
                             text_input="QUIT", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        while self.menu:
            game.clock.tick(game.fps)

            self.screen.blit(self.background, (0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(menu_text, menu_rect)

            for button in [play_button, how_to_play_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        game.menu = False
                        game.playing = True
                        return game
                    elif how_to_play_button.checkForInput(menu_mouse_pos):
                        self.how_to_play()
                    elif quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

        game.playing = True
        return game

    def end_game(self, game):

        menu_text = self.get_font(80).render("GAME OVER", True, "#00323d")
        menu_rect = menu_text.get_rect(center=(640, 100))

        score_label = Button(image=pygame.image.load("Main Menu Assets/score_rect.png"), pos=(640, 300),
                             text_input=f"SCORE: {game.score}", font=self.get_font(50), base_color="#FFFFFF",
                             hovering_color="White")

        restart_button = Button(image=pygame.image.load("Main Menu Assets/restart_rect.png"), pos=(640, 500),
                                text_input="RESTART", font=self.get_font(50), base_color="#FFFFFF",
                                hovering_color="Grey")

        main_menu = Button(image=pygame.image.load("Main Menu Assets/quit_rect.png"), pos=(640, 650),
                           text_input="MAIN MENU", font=self.get_font(50), base_color="#FFFFFF",
                           hovering_color="Grey")

        while not game.playing:

            game.clock.tick(game.fps)

            self.screen.blit(self.background, (0, 0))

            menu_mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(menu_text, menu_rect)

            for button in [restart_button, score_label, main_menu]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.checkForInput(menu_mouse_pos):
                        self.restart_game_button()
                    elif main_menu.checkForInput(menu_mouse_pos):
                        self.restart()

            pygame.display.update()

        game.playing = True
        return game

    def restart_game_button(self):
        menu = Menu()
        game = Game()
        game_loop(game)
        menu.end_game(game)

    def restart(self):
        menu = Menu()
        game = menu.main_menu()
        game_loop(game)
        menu.end_game(game)


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
        for plane in pl.Plane.__subclasses__():
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
                                plane_pos = (plane.x - plane.plane_img.get_rect().width / 2, plane.y - plane.plane_img.get_rect().height / 2)
                                other_pos = (other_plane.x - other_plane.plane_img.get_rect().width / 2, other_plane.y - other_plane.plane_img.get_rect().height / 2)
                                midpoint = (((plane_pos[0] + other_pos[0] - plane_warning.get_rect().height / 2)) / 2, ((plane_pos[1] + other_pos[1] - plane_warning.get_rect().height / 2)) / 2)
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
            # add a plane to the game at a random location every 20 seconds if there are less than 10 planes


def game_loop(game):
    # create a variable to keep track of the game l
    # create a loop to keep the game running
    while game.playing:
        game.clock.tick(game.fps)
        game.draw_objects() # draws all objects
        game.handle_collisions()
        game.event_loop()  # handles events
        game.update_planes()  # updates planes
        pygame.display.update()
    if not game.playing:
        game.draw_objects()
        game.handle_collisions()
        pygame.display.update()
        pygame.time.wait(3000)
    return


if __name__ == '__main__':
    menu = Menu()
    menu.restart()
