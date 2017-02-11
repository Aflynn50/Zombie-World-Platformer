# Imports
import os
import sys
import time

import pygame
from pygame.locals import *  # This allows me to reference certain variables without putting "pygame." first

import file_handling
import map
import player


class Game:

    pygame.init()  # Initiates the pygame module

    def __init__(self):
        self.FPS = 60  # Frames per second
        self.dt = 1 / self.FPS  # The time for each frame
        self.screen_size = list([500, 300])  # Screen size
        self.fp_leaderboard_folder = os.path.join("resources/leaderboard/")  # The fp in front of the files stands for file path
        self.fp_leaderboard = ""
        self.fp_icon = os.path.join("resources/sprites/game_icon.png")
        self.fp_level_folder = os.path.join("resources/maps/")
        self.level_folder_contents = file_handling.load_maps(os.path.join(self.fp_level_folder))  # This returns a list of the level names
        self.fp_key_bindings = os.path.join("resources/settings/key_bindings.txt")
        self.fp_settings = os.path.join("resources/settings/settings.txt")
        self.fp_music_main_theme = os.path.join("resources/sounds/foolboymedia_main_theme.wav")
        self.fp_music_menu = os.path.join("resources/sounds/foolboymedia_menu.wav")
        self.fp_soundfx_explosion = os.path.join("resources/sounds/explosion.wav")
        self.fp_soundfx_coin = os.path.join("resources/sounds/coin.wav")
        self.dict_keys = {"UP": pygame.K_UP, "DOWN": pygame.K_DOWN, "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT, "SHOOT": pygame.K_SPACE, "ENTER": pygame.K_RETURN, "BACKSPACE": pygame.K_BACKSPACE, "ALTUP": pygame.K_w, "ALTDOWN": pygame.K_s, "ALTLEFT": pygame.K_a, "ALTRIGHT": pygame.K_d}
        # A dictionary of each key and what it does, If you wanted to change a key binding you can do it here
        self.dict_keys = file_handling.key_bindings_read(self.fp_key_bindings, self.dict_keys)  # This calls the function to update the keybindings to what is in the settings file
        self.DISPLAYSURF = pygame.display.set_mode(self.screen_size)  # Creates the display surface object
        pygame.display.set_caption("Zombie World")  # Sets window caption
        pygame.display.set_icon(pygame.image.load(self.fp_icon))  # Sets window icon (in the bar at the top)
        self.menu1 = map.Menu(self.DISPLAYSURF, self.dt)  # Initialises new Menu object
        self.magneto_font = pygame.font.SysFont("magneto", 80)  # Create new font object
        self.sprites = list()

        self.bullets_group = pygame.sprite.Group()
        self.bullets = list()
        self.last_bullet = time.time()  # Sets variable to current time
        self.timer = time.time()
        self.score = 0
        self.game_over_flag = False
        self.FPSCLOCK = pygame.time.Clock()
        self._init_sounds()  # Calls function to load the sounds
        self.level = ""
        self.fp_map = self.menu()  # Calls the menu function which returns the map the user has selected
        self.screen = map.TiledRenderer(self.fp_map, self.DISPLAYSURF, self.dt)  # Loads the maps from the tmx file and initialises the map drawing object
        self.player1 = player.Player(self.dt, self.screen.player_pos, self.screen.map_size, self.screen.walls, self.screen.wall_type, self.dict_keys)  # Initialises a new player object
        self.sprites.append(self.player1)  # Adds the player sprite to the list of sprites to be displayed on the screen
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
        dict_settings = file_handling.settings_read(self.fp_settings)  # Checks configuration in the settings file
        self.music_on = False
        self.sound_on = False
        try:
            if dict_settings["MUSIC"] == "ON":
                self.music_on = True
            if dict_settings["SOUND"] == "ON":
                self.sound_on = True
        except KeyError:  # If the settings file does not have the sound or music setting an error will be displayed
            print("Settings file not correctly formatted, please sort it out")
            self.terminate()

    def run(self):
        self.FPSCLOCK = pygame.time.Clock()  # Starts the FPS counter
        self.timer = time.time()
        if self.music_on:
            self.music_main_theme.play(-1)

        while True:  # Infinite game loop
            self.check_for_quit()
            pygame.event.clear()  # Clears the event queue
            self.keys = pygame.key.get_pressed()  # Gets an list of which keys have been pressed and which have not
            self.game_over_flag = self.player1.update(self.keys)  # Updates the player sprite, returns "lose" if it has been killed
            self.bullets_group.update()  # Calls the update function on all the bullet objects in the group
            if self.game_over_flag == "lose":
                pygame.mixer.fadeout(500)  # Fades out the music over 500 ms
                self.game_over()  # Calls the game over function
                return True
            elif self.game_over_flag == "win":
                pygame.mixer.fadeout(500)
                self.win()
                return True

            if self.player1.bullet and (time.time() - self.last_bullet > 0.5):  # Checks if player has pressed the button to shoot a bullet and the time since the last one was shot is more then 0.2 seconds
                bullet = player.Bullet(self.dt, self.player1.player_position, self.player1.walls)  # Creates a new bullet object
                self.bullets.append(bullet)  # Adds the new bullet object to the list of active bullets (ones for which a collision with an enemy is checked)
                self.screen.group.add(self.bullets[-1])  # Adds the bullet to the list of sprites to be displayed on the screen
                self.bullets_group.add(self.bullets[-1])  # Adds the bullet to the group of bullets to be updated
                self.last_bullet = time.time()

            for zombie in self.screen.zombies:  # Cycles through each zombie in the list
                if not zombie.dead:
                    for bullet in self.bullets:  # Cycles through the list of bullets
                        if zombie.rect.colliderect(bullet):  # Checks if each bullet has hit a zombie
                            self.screen.group.remove(bullet)  # Removes the object from the list that will be displayed on the screen
                            self.bullets_group.remove(bullet)
                            self.bullets.remove(bullet)
                            zombie.dead = True
                            zombie.death_init()  # Initiates the death animation for the zombie
                            self.screen.group.remove(zombie)
                            self.screen.add_animation(zombie.death_animation_rects)
                            if self.sound_on:
                                self.soundfx_explosion.play()
                            self.score += 100  # Adds 100 to the score

                    if self.player1.rect.colliderect(zombie.animation_rect):  # Checks if the player has collided with a zombie
                        pygame.mixer.fadeout(500)
                        self.game_over()
                        return True

                    zombie.update()  # Updates the zombie

                else:
                    self.screen.group.remove(zombie)
                    self.screen.add_animation(zombie.death_animation_rects)  # Addes the death animation to the display group
                    zombie.death_update()

            for coin in self.screen.coins:  # Cycles through the active coins
                coin.update()
                if self.player1.rect.colliderect(coin.rect):  # Check if the player has touched the coin
                    if self.sound_on:
                        self.soundfx_coin.play()
                    self.screen.group.remove(coin)
                    self.screen.coins.remove(coin)
                    self.score += 100  # Adds 100 to the score if a coin has been collected

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
            self.menu1.update(self.DISPLAYSURF)  # Updates the menu display
            for event in pygame.event.get():  # Event handling loop
                if event.type == MOUSEBUTTONUP:
                    button_clicked = self.menu1.click(event.pos)  # Check which button has been clicked
                    if button_clicked == "Play":
                        map_selected = self.level_select()  # Open the level select screen which returns the map selected
                        if map_selected != "back":  # If the the back button has been pressed "back" is returned
                            pygame.mixer.fadeout(500)
                            return map_selected
                    elif button_clicked == "Exit":
                        self.terminate()
                    elif button_clicked == "Leaderboard":
                        self.leaderboard_level_select()
                    elif button_clicked == "Settings":
                        self.settings()

                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"]:  # When enter is pressed it is the same as pressing play
                        map_selected = self.level_select()
                        if map_selected != "back":
                            pygame.mixer.fadeout(500)
                            return map_selected

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def game_over(self):  # The function called when the player dies
        pygame.event.clear()
        if self.sound_on:
            self.soundfx_explosion.play()  # Plays an explosion sound when the player dies
        self.screen.add_animation(self.player1.death_animation_init_())  # Starts displaying the death animation blocks
        self.screen.remove_sprites(self.sprites)  # Stops displaying the player sprite
        self.timer = time.time() - self.timer  # Saves the current time in self.timer
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer, self.score)
            self.player1.death_animation_update()
            self.DISPLAYSURF.blit(self.magneto_font.render("Game over", 1, (0, 0, 0)), (20, 100))

            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"] or event.key == self.dict_keys["SHOOT"]:
                        return
                if event.type == MOUSEBUTTONUP:
                    return

            pygame.display.update()  # Transfers the display surface to the monitor
            self.FPSCLOCK.tick(self.FPS)

    def win(self):
        pygame.event.clear()
        self.screen.remove_sprites(self.sprites)  # Stops displaying the player sprite
        self.timer = time.time() - self.timer  # Saves the time since the game started into self.timer
        self.score += (self.screen.map_size[0] * 2) / self.timer
        #  The line above calculates the score to be added for the time the player got, it also depends on how long the level is
        while True:
            self.check_for_quit()
            self.screen.draw(self.DISPLAYSURF, self.player1, self.timer, self.score)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"]:
                        try:
                            if file_handling.leaderboard_check(self.fp_leaderboard_folder + self.level + ".txt")[10] < self.score:
                                #  The line above checks if the players score is in the top ten in the leaderboard
                                #  If it is then they will be asked to enter it into the scoreboard
                                self.leader_board_entry()
                        except IndexError:  # If there are less than 10 entries in the current leaderboard an Index error will be thrown and the player will be asked to enter their score
                            self.leader_board_entry()
                        return

            self.screen.win_update(self.DISPLAYSURF, self.score)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board_entry(self):  # This screen allows the user to input a name to be displayed on the leaderboard
        pygame.event.clear()
        name = ""
        while True:
            self.check_for_quit()
            for event in pygame.event.get():  # Checks what keys have been pressed
                if event.type == KEYUP:
                    if event.key == self.dict_keys["ENTER"] and len(name) > 0:  # Checks if there is anything written in the box when they press enter
                        self.fp_leaderboard = self.fp_leaderboard_folder + self.level + ".txt"  # Generates the name of the leaderboard for the current level
                        file_handling.leaderboard_add(self.fp_leaderboard, name, int(self.score))  # Calls the function to add the name to the leaderboard file
                        return
                    elif event.key == self.dict_keys["BACKSPACE"]:  # If backspace is pressed the last letter in the name is deleted
                        name = name[:(len(name) - 1)]
                    elif len(name) < 4 and event.key <= 127:
                        # Checks if the length of the name that has already been inputted is less than 4 and the character code is less than 128 (This stops the user entering characters that have not got an image in the font file)
                        if chr(event.key).isalpha():  # Checks it is not a number that has been pressed
                            name += chr(event.key).capitalize()

            self.screen.enter_score(self.DISPLAYSURF, name)
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def leader_board(self):
        pygame.event.clear()
        leaderboard = file_handling.leaderboard_read(self.fp_leaderboard)  # Calls the file handling function to fetch the leaderboard from the file as a list
        scroll_position = 0  # The scroll position is what dictates which part of the list is displayed on the screen
        while True:
            self.check_for_quit()
            self.menu1.display_leaderboard(self.DISPLAYSURF, leaderboard, scroll_position)  # Calls the function to display the leaderboard
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if (event.key == self.dict_keys["UP"] or event.key == self.dict_keys["ALTUP"]) and scroll_position > 0:  # The user can scroll up and down the leaderboard list with the up and down keys
                        scroll_position -= 1
                    elif (event.key == self.dict_keys["DOWN"] or event.key == self.dict_keys["ALTDOWN"]) and scroll_position < (len(leaderboard) - 1):
                        scroll_position += 1
                    elif event.key == self.dict_keys["BACKSPACE"]:
                        return

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def settings(self):
        pygame.event.clear()
        self.menu1._init_settings(self.fp_settings)  # Initiates the display module for settings
        while True:
            mouse_pos = (0, 0)
            self.check_for_quit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    mouse_pos = event.pos
                    if self.menu1.save_button.click(event.pos):  # Checks if the save button has been pressed
                        file_handling.settings_update(self.fp_settings, self.menu1.dict_settings)  # Writes to the settings file
                        if self.menu1.dict_settings["MUSIC"] == "ON":  # If the music has been switched on it starts playing
                            if not pygame.mixer.get_busy():
                                self.music_menu.play(-1)
                        else:  # If the music has been switched off it stops playing
                            pygame.mixer.fadeout(500)
                        self._init_sounds()
                        return
                if event.type == KEYUP:
                    if event.key == self.dict_keys["BACKSPACE"]:  # If backspace is pressed it goes back to the menu without saving
                        return

            self.menu1.display_settings(self.DISPLAYSURF, mouse_pos)  # Draws the settings screen

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def level_select(self):
        pygame.event.clear()
        self.menu1._init_levels(self.level_folder_contents)  # Initiates the level select module
        scroll_position = 0
        while True:
            self.check_for_quit()
            self.menu1.display_levels(self.DISPLAYSURF, scroll_position, "play")  # Displays the levels in the game files
            level_buttons = self.menu1.level_buttons  # Fetches the level buttons from the display module
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    try:
                        for button in level_buttons[scroll_position: scroll_position + 4]:  # Runs through the list of buttons currently on the screen
                            if button.click(event.pos):  # Checks if the buttons have been pressed
                                self.level = button.text
                                return self.fp_level_folder + button.text + ".tmx"  # Returns the file path
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

if __name__ == "__main__":  # Checks if this file has been run by a user, if it hasn't the game won't run
    while True:
        newgame = Game()  # Initialises the game object
        newgame.run()  # Runs game forever
