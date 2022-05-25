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
                obj.length_of_movements = 0
            self.holding = True
        if self.holding:
            if holding:
                if obj.movements:
                    # add the length between the current and next point to obj.length_of_movements
                    obj.length_of_movements += math.sqrt(
                        (obj.movements[-1][0] - self.x) ** 2 + (obj.movements[-1][1] - self.y) ** 2)
                    if obj.length_of_movements < 1000:
                        # get center of obj.plane_img
                        if obj.movements[-1] != (self.x, self.y):
                            obj.movements.append((self.x, self.y))
                            return
                if obj.length_of_movements < 1000:
                    obj.movements.append((self.x, self.y))
            else:
                obj.movements.pop()
                self.holding = False


class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
