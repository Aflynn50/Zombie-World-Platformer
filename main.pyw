import os
import sys
import time

import pygame
from pygame.locals import *

import file_handling
import map
import player


class Game:

    pygame.init()

    def __init__(self):
        self.FPS = 60
        self.dt = 1 / self.FPS  # The time for each frame
        self.screen_size = list([500, 300])  # Screen size
        self.fp_leaderboard_folder = os.path.join("resources/leaderboard/")
        self.fp_leaderboard = ""
        self.fp_icon = os.path.join("resources/sprites/game_icon.png")
        self.fp_level_folder = os.path.join("resources/maps/")

        self.level_folder_contents = file_handling.load_maps(os.path.join(self.fp_level_folder))

        self.fp_key_bindings = os.path.join("resources/settings/key_bindings.txt")
        self.fp_settings = os.path.join("resources/settings/settings.txt")
        self.fp_music_main_theme = os.path.join("resources/sounds/foolboymedia_main_theme.wav")
        self.fp_music_menu = os.path.join("resources/sounds/foolboymedia_menu.wav")
        self.fp_soundfx_explosion = os.path.join("resources/sounds/explosion.wav")
        self.fp_soundfx_coin = os.path.join("resources/sounds/coin.wav")
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
        self.FPSCLOCK = pygame.time.Clock()
        self._init_sounds()
        self.level = ""
        self.fp_map = self.menu()
        self.screen = map.TiledRenderer(self.fp_map, self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file and initialises the map drawing object
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type, self.dict_keys)  # Initialises a new player object
        self.sprites.append(self.player1)
        self.screen.add_sprites(self.sprites)  # Adds the list of sprites to the list of things to be displayed by the renderer
        self.keys = None



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

    def _init_sounds(self):  # Loads music and sounds
        pygame.mixer.init()  # Initiates the pygame sounds module
        self.music_main_theme = pygame.mixer.Sound(self.fp_music_main_theme)
        self.music_menu = pygame.mixer.Sound(self.fp_music_menu)
        self.music_menu.set_volume(0.5)
        self.soundfx_coin = pygame.mixer.Sound(self.fp_soundfx_coin)
        self.soundfx_coin.set_volume(0.5)
        self.soundfx_explosion = pygame.mixer.Sound(self.fp_soundfx_explosion)
        self.soundfx_explosion.set_volume(0.5)
        dict_settings = file_handling.settings_read(self.fp_settings)
        self.music_on = False
        self.sound_on = False
        try:
            if dict_settings["MUSIC"] == "ON":
                self.music_on = True
            if dict_settings["SOUND"] == "ON":
                self.sound_on = True
        except KeyError:
            print("Settings file not correctly formatted, please sort it out")
            self.terminate()

    def run(self):
        self.FPSCLOCK = pygame.time.Clock()  # Starts the FPS counter
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
                bullet = player.Bullet(self.dt, self.player1.player_position, self.player1.walls)
                self.bullets.append(bullet)
                self.screen.group.add(self.bullets[-1])
                self.bullets_group.add(self.bullets[-1])
                self.last_bullet = time.time()

            #self.screen.draw(self.DISPLAYSURF, self.player1, (time.time() - self.timer), self.score)  # Updates the screen
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
                            if self.sound_on:
                                self.soundfx_explosion.play()
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
                if self.player1.rect.colliderect(coin.rect):
                    if self.sound_on:
                        self.soundfx_coin.play()
                    self.screen.group.remove(coin)
                    self.screen.coins.remove(coin)
                    self.score += 100

            self.screen.draw(self.DISPLAYSURF, self.player1, (time.time() - self.timer),
                             self.score)  # Updates the screen
            self.check_for_quit()
            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def menu(self):
        pygame.event.clear()
        if self.music_on:
            self.music_menu.play(-1)
        while True:
            self.check_for_quit()
            self.menu1.update(self.DISPLAYSURF)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    button_clicked = self.menu1.click(event.pos)
                    if button_clicked == "Play":
                        map = self.level_select()
                        if map != "back":
                            self.music_menu.fadeout(500)
                            return map
                    elif button_clicked == "Exit":
                        self.terminate()
                    elif button_clicked == "Leaderboard":
                        self.leaderboard_level_select()
                    elif button_clicked == "Settings":
                        self.settings()

                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"]:
                        map = self.level_select()
                        if map != "back":
                            self.music_menu.fadeout(500)
                            return map

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def game_over(self):
        pygame.event.clear()
        if self.sound_on:
            self.soundfx_explosion.play()
        self.screen.add_animation(self.player1.death_animation_init_())
        self.screen.remove_sprites(self.sprites)
        self.timer = time.time() - self.timer
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer, self.score)
            self.player1.death_animation_update()
            self.DISPLAYSURF.blit(self.magneto_font.render("Game over", 1, (0, 0, 0)), (20, 100))

            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"]:
                        return

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def win(self):
        pygame.event.clear()
        self.screen.remove_sprites(self.sprites)
        self.timer = time.time() - self.timer
        self.score += self.screen.map_size[0] / self.timer

        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer, self.score)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"]:
                        try:
                            if file_handling.leaderboard_check(self.fp_leaderboard_folder + self.level + ".txt")[10] < self.score:
                                self.leader_board_entry()
                        except IndexError:
                            self.leader_board_entry()
                        return

            self.screen.win_update(self.DISPLAYSURF, self.score)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board_entry(self):
        pygame.event.clear()
        name = ""
        while True:
            self.check_for_quit()
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"] and len(name) > 0:
                        self.fp_leaderboard = self.fp_leaderboard_folder + self.level + ".txt"
                        file_handling.leaderboard_add(self.fp_leaderboard, name, int(self.score))
                        return
                    elif event.key == self.dict_keys["BACKSPACE"]:
                        name = name[:(len(name) - 1)]
                    elif len(name) < 4 and event.key <= 127:
                        if chr(event.key).isalpha():
                            name += chr(event.key).capitalize()

            self.screen.enter_score(self.DISPLAYSURF, name)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board(self):
        pygame.event.clear()
        leaderboard = file_handling.leaderboard_read(self.fp_leaderboard)
        scroll_position = 0
        while True:
            self.check_for_quit()
            self.menu1.display_leaderboard(self.DISPLAYSURF, leaderboard, scroll_position)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if (event.key == self.dict_keys["UP"]) and scroll_position > 0:
                        scroll_position -= 1
                    elif (event.key == self.dict_keys["DOWN"]) and scroll_position < (len(leaderboard) - 1):
                        scroll_position += 1
                    elif event.key == self.dict_keys["BACKSPACE"]:
                        return

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def settings(self):
        pygame.event.clear()
        self.menu1._init_settings(self.fp_settings)
        while True:
            mouse_pos = (0, 0)
            self.check_for_quit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    mouse_pos = event.pos
                    if self.menu1.settings_button.click(event.pos):
                        if self.menu1.dict_settings["MUSIC"] == "ON":
                            if not pygame.mixer.get_busy():
                                self._init_sounds()
                                self.music_menu.play(-1)
                        else:
                            pygame.mixer.fadeout(500)
                        file_handling.settings_update(self.fp_settings, self.menu1.dict_settings)
                        return
                if event.type == KEYUP:
                    if event.key == self.dict_keys["BACKSPACE"]:
                        return

            self.menu1.display_settings(self.DISPLAYSURF, mouse_pos)

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def level_select(self):
        pygame.event.clear()
        self.menu1._init_levels(self.level_folder_contents)
        scroll_position = 0
        while True:
            self.check_for_quit()
            self.menu1.display_levels(self.DISPLAYSURF, scroll_position, "play")
            level_buttons = self.menu1.level_buttons
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    try:
                        for button in level_buttons[scroll_position: scroll_position + 4]:
                            if button.click(event.pos):
                                self.level = button.text
                                return self.fp_level_folder + button.text + ".tmx"
                    except IndexError:
                        pass
                if event.type == KEYUP:
                    if (event.key == self.dict_keys["UP"]) and scroll_position > 0:
                        scroll_position -= 1
                    elif (event.key == self.dict_keys["DOWN"]) and scroll_position < (len(level_buttons) - 1):
                        scroll_position += 1
                    if event.key == self.dict_keys["BACKSPACE"]:
                        return "back"
                    if event.key == self.dict_keys["ENTER"]:
                        mouse_pos = pygame.mouse.get_pos()
                        try:
                            for button in level_buttons[scroll_position: scroll_position + 4]:
                                if button.click(mouse_pos):
                                    self.level = button.text
                                    return self.fp_level_folder + button.text + ".tmx"
                        except IndexError:
                            pass

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leaderboard_level_select(self):
        pygame.event.clear()
        self.menu1._init_levels(self.level_folder_contents)
        scroll_position = 0
        while True:
            self.check_for_quit()
            self.menu1.display_levels(self.DISPLAYSURF, scroll_position, "leaderboard")
            level_buttons = self.menu1.level_buttons
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    try:
                        for button in level_buttons[scroll_position: scroll_position + 4]:
                            if button.click(event.pos):
                                self.fp_leaderboard = self.fp_leaderboard_folder + button.text + ".txt"
                                self.leader_board()
                    except IndexError:
                        pass
                if event.type == KEYUP:
                    if (event.key == self.dict_keys["UP"]) and scroll_position > 0:
                        scroll_position -= 1
                    elif (event.key == self.dict_keys["DOWN"]) and scroll_position < (len(level_buttons) - 1):
                        scroll_position += 1
                    if event.key == self.dict_keys["BACKSPACE"]:
                        return
                    if event.key == self.dict_keys["ENTER"]:
                        mouse_pos = pygame.mouse.get_pos()
                        try:
                            for button in level_buttons[scroll_position: scroll_position + 4]:
                                if button.click(mouse_pos):
                                    self.fp_leaderboard = self.fp_leaderboard_folder + button.text + ".txt"
                                    self.leader_board()
                        except IndexError:
                            pass

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)


while True:
    newgame = Game()  # Initialises the game object
    newgame.run()  # Runs game forever
