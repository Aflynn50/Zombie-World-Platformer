import pygame
import sys
import time
import os
import math
import collision
import map
import player
from pygame.locals import *
from pygame import gfxdraw


class Game:

    pygame.init()


    def __init__(self):
        self.FPS = 60
        self.dt = 1 / self.FPS  # The time for each frame
        self.screen_size = list([500, 300])
        self.DISPLAYSURF = pygame.display.set_mode(self.screen_size)  # Creates the display surface object
        pygame.display.set_caption("Zombie World")
        self.game_over_font = pygame.font.SysFont("magneto", 80)
        self.sprites = list()
        self.screen = map.TiledRenderer(os.path.join("resources/maps/map8.tmx"), self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type)
        self.sprites.append(self.player1)
        self.screen.add_sprites(self.sprites)
        self.game_over_animation_rect = pygame.Rect(0, 0, self.screen_size[0], 0)
        self.keys = 0
        self.animation_finished = False

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
        self.menu()
        while True:
            self.screen.draw(self.DISPLAYSURF, self.player1)  # Updates the screen
            self.check_for_quit()
            #pygame.gfxdraw.pixel(self.DISPLAYSURF, 1, 1, (0, 0, 0))
            self.keys = pygame.key.get_pressed()
            self.player1.update(self.keys)
            for zombie in self.screen.zombies:
                if pygame.sprite.collide_rect(self.player1, zombie):
                    self.game_over()
                zombie.update()
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def menu(self):
        menu1 = map.Menu(self.DISPLAYSURF)
        while True:
            self.check_for_quit()
            self.keys = pygame.key.get_pressed()
            menu1.update(self.DISPLAYSURF)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    if menu1.click(event.pos):
                        return
                elif self.keys[pygame.K_RETURN]:
                    return
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def game_over(self):
        while True:
            self.check_for_quit()
            pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), self.game_over_animation_rect)

            if self.game_over_animation_rect.h > self.screen_size[1] and not self.animation_finished:
                self.animation_finished = True
            elif not self.animation_finished:
                self.game_over_animation_rect.h += 8
            else:
                self.DISPLAYSURF.blit(self.game_over_font.render("Game over", 1, (255, 255, 255)), (20, 100))

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)



newgame = Game()
newgame.run()
