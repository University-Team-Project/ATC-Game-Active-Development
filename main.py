import json
import sys
import time
import random
from game import *
from levels import *
import plane as pl

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

    def main_menu(self, passed_game=None):
        if passed_game:
            return passed_game
        menu_text = self.get_font(100).render("MAIN MENU", True, '#00323d')
        menu_rect = menu_text.get_rect(center=(640, 100))

        play_button = Button(image=pygame.image.load("Main Menu Assets/Play Rect.png"), pos=(640, 230),
                             text_input="PLAY", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        how_to_play_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 360),
                                    text_input="TUTORIAL", font=self.get_font(64), base_color="#d7fcd4",
                                    hovering_color="Grey")
        settings_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 500),
                                    text_input="SETTINGS", font=self.get_font(64), base_color="#d7fcd4",
                                    hovering_color="Grey")
        quit_button = Button(image=pygame.image.load("Main Menu Assets/Quit Rect.png"), pos=(640, 630),
                             text_input="QUIT", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        while self.menu:
            self.clock.tick(self.fps)

            self.screen.blit(self.background, (0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(menu_text, menu_rect)

            for button in [play_button, how_to_play_button, settings_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        game = self.gamemode()
                    elif settings_button.checkForInput(menu_mouse_pos):
                        self.settings()
                    elif how_to_play_button.checkForInput(menu_mouse_pos):
                        self.how_to_play()
                    elif quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

        return game

    def gamemode(self):
        menu_text = self.get_font(100).render("GAMEMODE:", True, '#00323d')
        menu_rect = menu_text.get_rect(center=(640, 100))

        standard_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 230),
                             text_input="STANDARD", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        advanced_button = Button(image=pygame.image.load("Main Menu Assets/Tutorial Rect.png"), pos=(640, 360),
                                    text_input="ADVANCED", font=self.get_font(64), base_color="#d7fcd4",
                                    hovering_color="Grey")
        back_button = Button(image=pygame.image.load("Main Menu Assets/Quit Rect.png"), pos=(640, 630),
                             text_input="BACK", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")

        while self.menu:
            self.clock.tick(self.fps)

            self.screen.blit(self.background, (0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(menu_text, menu_rect)

            for button in [standard_button, advanced_button, back_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if standard_button.checkForInput(menu_mouse_pos):
                        game = Game()
                        self.menu = False
                        return game
                    elif advanced_button.checkForInput(menu_mouse_pos):
                        game = Level()
                        self.menu = False
                        return game
                    elif back_button.checkForInput(menu_mouse_pos):
                        return

            pygame.display.update()

        return game

    def how_to_play(self):
        how_to_play_text = self.get_font(45).render("This is the TUTORIAL screen.", True, "Black")
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

    def settings(self):
        settings_text = self.get_font(100).render("SETTINGS", True, '#00323d')
        settings_rect = settings_text.get_rect(center=(640, 100))
        settings_back = Button(image=pygame.image.load("Main Menu Assets/Quit Rect.png"), pos=(640, 630),
                             text_input="BACK", font=self.get_font(64), base_color="#d7fcd4",
                             hovering_color="Grey")
        while True:
            options_mouse_pos = pygame.mouse.get_pos()
            # blit the background image
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(settings_text, settings_rect)
            settings_back.changeColor(options_mouse_pos)
            settings_back.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if settings_back.checkForInput(options_mouse_pos):
                        return

            pygame.display.update()

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
                        game.reset()
                        self.restart(game)
                    elif main_menu.checkForInput(menu_mouse_pos):
                        menu = Menu()
                        menu.start()

            pygame.display.update()

        game.playing = True
        return game

    def restart_game_button(self):
        menu = Menu()
        game = self.main_menu()
        game.loop(game)
        menu.end_game(game)

    def start(self):
        game = self.main_menu()
        game.game_loop()
        self.end_game(game)

    def restart(self, game):
        game = self.main_menu(game)
        game.game_loop()
        self.end_game(game)


if __name__ == '__main__':
    menu = Menu()
    menu.start()
