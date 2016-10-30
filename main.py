import pygame
import sys
import time
import os
import random
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
        pygame.display.set_icon(pygame.image.load("resources/sprites/game_icon.png"))
        self.magneto_font = pygame.font.SysFont("magneto", 80)
        self.sprites = list()
        self.screen = map.TiledRenderer(os.path.join("resources/maps/map8.tmx"), self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type)
        self.sprites.append(self.player1)
        self.screen.add_sprites(self.sprites)
        self.animation_counter = 0
        self.animation_group = pygame.sprite.Group()
        self.keys = 0

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

            self.check_for_quit()
            self.keys = pygame.key.get_pressed()
            self.game_over_flag = self.player1.update(self.keys)
            if self.game_over_flag == "lose":
                self.game_over()
                return True
            elif self.game_over_flag == "win":
                self.win()
                return True

            self.screen.draw(self.DISPLAYSURF, self.player1)  # Updates the screen
            for zombie in self.screen.zombies:
                zombie.update()
                if self.player1.rect.colliderect(zombie.animation_rect):
                    self.game_over()
                    return True

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
                    button_clicked = menu1.click(event.pos)
                    if button_clicked == "play":
                        return
                    elif button_clicked == "exit":
                        self.terminate()

                elif self.keys[pygame.K_RETURN]:
                    return
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def game_over(self):
        self.screen.add_animation(self.player1.death_animation_init_())
        self.screen.remove_sprites(self.sprites)
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1)
            self.player1.death_animation_update(self.DISPLAYSURF)

            """
            pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), self.game_over_animation_rect)

            if self.game_over_animation_rect.h > self.screen_size[1] and not self.animation_finished:
                self.animation_finished = True
            elif not self.animation_finished:
                self.game_over_animation_rect.h += 4
            else:
                self.DISPLAYSURF.blit(self.magneto_font.render("Game over", 1, (255, 255, 255)), (20, 100))
            """

            self.DISPLAYSURF.blit(self.magneto_font.render("Game over", 1, (0, 0, 0)), (20, 100))

            self.keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if self.keys[pygame.K_RETURN]:
                    return

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def win(self):
        self.screen.remove_sprites(self.sprites)
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1)
            if self.animation_counter % self.FPS == 0:
                position = random.randint(0, self.screen_size[0]), random.randint(0, self.screen_size[1])
                for block in range(50):
                    self.animation_group.add(player.AnimationRect(position, (4, 4), self.dt))
            self.animation_group.update(self.DISPLAYSURF)
            self.animation_group.draw(self.DISPLAYSURF)
            self.animation_counter += 1
            self.DISPLAYSURF.blit(self.magneto_font.render("You win", 1, (0, 0, 0)), (85, 100))

            self.keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if self.keys[pygame.K_RETURN]:
                    return

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)


newgame = Game()
gameOver = newgame.run()
while True:
    if gameOver:
        newgame = Game()
        gameOver = newgame.run()
