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
        self.bullets_group = pygame.sprite.Group()
        self.bullets = list()
        self.last_bullet = time.time()
        self.timer = time.time()
        self.score = 0
        self.game_over_flag = False
        self.screen = map.TiledRenderer(os.path.join("resources/maps/map8.tmx"), self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type)
        self.sprites.append(self.player1)
        self.screen.add_sprites(self.sprites)
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
            if event.key == K_ESCAPE or event.key == K_BACKSPACE:
                self.terminate()  # Calls the function to shut down the program
            pygame.event.post(event)  # put the other KEYUP event objects back

    def run(self):
        self.FPSCLOCK = pygame.time.Clock()  # Starts the FPS counter
        self.menu()
        self.timer = time.time()

        while True:
            self.check_for_quit()
            self.keys = pygame.key.get_pressed()
            self.game_over_flag = self.player1.update(self.keys)
            self.bullets_group.update()
            if self.game_over_flag == "lose":
                self.game_over()
                return True
            elif self.game_over_flag == "win":
                self.win()
                return True

            if self.player1.bullet and (time.time() - self.last_bullet > 2):
                bullet = player.Bullet(self.dt, self.player1.player_position)
                self.bullets.append(bullet)
                self.screen.group.add(self.bullets[-1])
                self.bullets_group.add(self.bullets[-1])
                self.last_bullet = time.time()

            self.screen.draw(self.DISPLAYSURF, self.player1, (time.time() - self.timer))  # Updates the screen
            for zombie in self.screen.zombies:
                if not zombie.dead:
                    for bullet in self.bullets:
                        if zombie.rect.colliderect(bullet):
                            self.screen.group.remove(bullet)
                            self.bullets_group.remove(bullet)
                            self.bullets.remove(bullet)
                            zombie.dead = True
                            zombie.death_init()
                            self.screen.group.remove(zombie)
                            self.screen.add_animation(zombie.death_animation_rects)
                            self.score += 100

                    if self.player1.rect.colliderect(zombie.animation_rect):
                        self.game_over()
                        return True

                    zombie.update()

                else:
                    self.screen.group.remove(zombie)
                    self.screen.add_animation(zombie.death_animation_rects)
                    zombie.death_update()

            self.check_for_quit()
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
        self.timer = time.time() - self.timer
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer)
            self.player1.death_animation_update()
            self.DISPLAYSURF.blit(self.magneto_font.render("Game over", 1, (0, 0, 0)), (20, 100))

            self.keys = pygame.key.get_pressed()
            #for event in pygame.event.get():
            if self.keys[pygame.K_RETURN]:
                return

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def win(self):
        self.screen.remove_sprites(self.sprites)
        self.timer = time.time() - self.timer
        self.score += (1 / self.timer) * 3000

        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer)

            self.keys = pygame.key.get_pressed()
            if self.keys[pygame.K_RETURN]:
                return

            self.screen.win_update(self.DISPLAYSURF, self.score)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)


newgame = Game()
gameOver = newgame.run()
while True:
    if gameOver:
        newgame = Game()
        gameOver = newgame.run()
