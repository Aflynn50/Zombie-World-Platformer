import pygame
import sys
import time
import os
import math
import pytmx
import collision
import map
import player
from pygame.locals import *


class Game:

    pygame.init()

    def __init__(self):
        self.FPS = 60
        self.dt = 1 / self.FPS  # The time for each frame
        self.DISPLAYSURF = pygame.display.set_mode((500, 300))  # Creates the display surface object
        self.player1 = player.Player(self.dt)
        self.screen = map.TiledRenderer(os.path.join("resources/maps/map6.tmx"), self.DISPLAYSURF, self.player1)  # Loads the maps from the tmx file
        self.player1.walls = self.screen.walls  # Take the walls data from the screen object and transfers it to player
        self.player1.map_height = self.screen.tmx_data.height * self.screen.tmx_data.tileheight  # Transfes the screen width and hight to the player object
        self.player1.map_width = self.screen.tmx_data.width * self.screen.tmx_data.tilewidth
        self.player1.rect.x = self.screen.player_pos[0]
        self.player1.rect.y = self.screen.player_pos[1]

    @staticmethod
    def terminate():  # Shuts down the pygame module and the sys module and
        pygame.quit()
        sys.exit()

    def check_for_quit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            if event.type == QUIT:
                self.terminate()  # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):  # Check what keys have been released
            if event.key == K_ESCAPE:
                self.terminate()  # Calls the function to shut down the program
            pygame.event.post(event)  # put the other KEYUP event objects back

    def run(self):
        self.FPSCLOCK = pygame.time.Clock()  # Starts the FPS counter

        while True:
            self.screen.draw(self.DISPLAYSURF, self.player1)  # Updates the screen
            self.check_for_quit()
            self.player1.update(pygame.key.get_pressed())
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)


newgame = Game()
newgame.run()
