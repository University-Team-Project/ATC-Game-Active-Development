import pygame
from pygame import *
import math


class Menu:
    def __init__(self):
        """
        :initialises all the values to be used for game settings / rules
        """
        pygame.init()
        self.fps = 240
        self.caption = 'Flight Control'
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('Assets/menu.png'), (1280, 720)).convert()
        self.objects = []

        pygame.display.set_caption(self.caption)
        pygame.mouse.set_visible(False)
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def draw_objects(self):
        # draw the background image
        self.screen.blit(self.background, (0, 0))
        if self.objects:
            for obj in self.objects:
                obj.draw(self.screen)


class Cursor:
    def __init__(self):
        """
        initialises all the data to be used for handling the cursor and its actions
        """
        self.x = 0
        self.y = 0
        self.holding = False

    def set_path(self, holding, obj=None):

        """
        :param obj:
        :param holding:
        :return handles the movement of the rectangle on screen according to the mouse actions:
        """
        self.x, self.y = pygame.mouse.get_pos()
        if obj:
            if obj.new_select:
                obj.new_select = False
                obj.movements = []
            self.holding = True
        if self.holding:
            if holding:
                if obj.movements:
                    # get center of obj.plane_img
                    if obj.movements[-1] != (self.x, self.y):
                        obj.movements.append((self.x, self.y))
                        return
                obj.movements.append([self.x, self.y])
            else:
                obj.movements.pop()
                self.holding = False
