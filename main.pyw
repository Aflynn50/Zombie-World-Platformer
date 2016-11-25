import pygame
import sys
import time
import os
import random
import math
import collision
import enemies
import map
import player
import file_handling
from pygame.locals import *
from pygame import gfxdraw


class Game:

    pygame.init()

    def __init__(self):
        self.FPS = 60
        self.dt = 1 / self.FPS  # The time for each frame
        self.screen_size = list([500, 300])  # Screen size
        self.fp_leaderboard = os.path.join("resources/leaderboard/leaderboard.txt")
        self.fp_icon = os.path.join("resources/sprites/game_icon.png")
        self.fp_map = os.path.join("resources/maps/map8.tmx")
        self.fp_key_bindings = os.path.join("resources/settings/key_bindings.txt")
        self.fp_music_main_theme = os.path.join("resources/sounds/foolboymedia_main_theme.wav")
        self.fp_music_menu = os.path.join("resources/sounds/foolboymedia_menu.wav")
        self.dict_keys = {"UP": pygame.K_UP, "DOWN": pygame.K_DOWN, "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT, "SHOOT": pygame.K_SPACE, "ENTER": pygame.K_RETURN, "BACKSPACE": pygame.K_BACKSPACE}
        self.dict_keys = file_handling.key_bindings_read(self.fp_key_bindings, self.dict_keys)
        self.DISPLAYSURF = pygame.display.set_mode(self.screen_size)  # Creates the display surface object
        pygame.display.set_caption("Zombie World")  # Sets window caption
        pygame.display.set_icon(pygame.image.load(self.fp_icon))  # Sets window icon (in the bar at the top)
        self.menu1 = map.Menu(self.DISPLAYSURF, self.dt)  # Initialises new Menu object
        self.magneto_font = pygame.font.SysFont("magneto", 80)  # Create new font object
        self.sprites = list()
        self.bullets_group = pygame.sprite.Group()
        self.bullets = list()
        self.last_bullet = time.time()
        self.timer = time.time()
        self.score = 0
        self.game_over_flag = False
        self.screen = map.TiledRenderer(self.fp_map, self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file and initialises the map drawing object
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type, self.dict_keys)  # Initialises a new player object
        self.sprites.append(self.player1)
        self.screen.add_sprites(self.sprites)  # Adds the list of sprites to the list of things to be displayed by the renderer
        self.keys = 0
        pygame.mixer.init()
        self.music_main_theme = pygame.mixer.Sound(self.fp_music_main_theme)
        self.music_menu = pygame.mixer.Sound(self.fp_music_menu)
        self.music_menu.set_volume(0.5)
        self.music_on = False


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
        self.timer = time.time()
        if self.music_on:
            self.music_main_theme.play(-1)

        while True:
            self.check_for_quit()
            pygame.event.clear()
            self.keys = pygame.key.get_pressed()
            self.game_over_flag = self.player1.update(self.keys)
            self.bullets_group.update()
            if self.game_over_flag == "lose":
                self.music_main_theme.fadeout(500)
                self.game_over()
                return True
            elif self.game_over_flag == "win":
                self.music_main_theme.fadeout(500)
                self.win()
                return True

            if self.player1.bullet and (time.time() - self.last_bullet > 0.2):
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
                        self.music_main_theme.fadeout(500)
                        self.game_over()
                        return True

                    zombie.update()

                else:
                    self.screen.group.remove(zombie)
                    self.screen.add_animation(zombie.death_animation_rects)
                    zombie.death_update()

            for coin in self.screen.coins:
                coin.update()

            self.check_for_quit()
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def menu(self):
        if self.music_on:
            self.music_menu.play(-1)
        while True:
            self.check_for_quit()
            self.keys = pygame.key.get_pressed()
            self.menu1.update(self.DISPLAYSURF)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    button_clicked = self.menu1.click(event.pos)
                    if button_clicked == "Play":
                        self.music_menu.fadeout(500)
                        return
                    elif button_clicked == "Exit":
                        self.terminate()
                    elif button_clicked == "Leaderboard":
                        self.leader_board()
                    elif button_clicked == "Settings":
                        self.settings()

                elif self.keys[self.dict_keys["ENTER"]]:
                    self.music_menu.fadeout(500)
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
            if self.keys[self.dict_keys["ENTER"]]:
                return

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def win(self):
        self.screen.remove_sprites(self.sprites)
        self.timer = time.time() - self.timer
        self.score += (1 / self.timer) * 3000

        while True:
            enter_score = False
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer)
            for event in pygame.event.get(KEYUP):
                if event.key == self.dict_keys["ENTER"]:
                    try:
                        if file_handling.leaderboard_check(self.fp_leaderboard)[10] < self.score:
                            self.leader_board_entry()
                    except IndexError:
                        self.leader_board_entry()
                    return

            self.screen.win_update(self.DISPLAYSURF, self.score)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board_entry(self):
        name = ""
        while True:
            self.check_for_quit()
            for event in pygame.event.get(KEYUP):
                if event.key == self.dict_keys["ENTER"] and len(name) > 0:
                    file_handling.leaderboard_add(self.fp_leaderboard, name, int(self.score))
                    return
                elif event.key == self.dict_keys["BACKSPACE"]:
                    print("a")
                    name = name[:(len(name) - 1)]
                elif len(name) < 4 and event.key <= 127:
                    if chr(event.key).isalpha():
                        name += chr(event.key).capitalize()

            self.screen.enter_score(self.DISPLAYSURF, name)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board(self):
        leaderboard = file_handling.leaderboard_read(self.fp_leaderboard)
        scroll_position = 0
        while True:
            self.check_for_quit()
            self.menu1.display_leaderboard(self.DISPLAYSURF, leaderboard, scroll_position)
            for event in pygame.event.get(KEYUP):
                if (event.key == self.dict_keys["UP"]) and scroll_position > 0:
                    scroll_position -= 1
                elif (event.key == self.dict_keys["DOWN"]) and scroll_position < (len(leaderboard) - 1):
                    scroll_position += 1

            self.keys = pygame.key.get_pressed()
            if self.keys[self.dict_keys["BACKSPACE"]]:
                return
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def settings(self):
        while True:
            mouse_pos = (0, 0)
            self.check_for_quit()
            for event in pygame.event.get(MOUSEBUTTONUP):
                mouse_pos = event.pos

            self.menu1.display_settings(self.DISPLAYSURF, mouse_pos)
            self.keys = pygame.key.get_pressed()
            if self.keys[self.dict_keys["BACKSPACE"]]:
                return

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)


newgame = Game()  # Initialises the game object
gameOver = newgame.run()  # Runs game
while True:
    newgame = Game()
    gameOver = newgame.run()
