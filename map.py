import pygame
import sys
import time
import os
import math
import random
import enemies
import player
from pytmx import *
from pytmx.util_pygame import load_pygame
from pygame.locals import *
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup


class TiledRenderer(object):

    def __init__(self, filename, surface, dt):
        tm = load_pygame(filename)
        self.dt = dt
        self.FPS = 1 / self.dt
        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.map_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        self.win_animation_counter = 0
        self.win_animation_group = pygame.sprite.Group()
        # setup level geometry with simple pygame rects, loaded from pytmx
        self.timer_font = pygame.font.SysFont("haettenschweiler", 25)
        self.magneto_font = pygame.font.SysFont("magneto", 60)
        self.walls = list()
        self.wall_type = list()
        self.zombies = list()

        for wall in self.tmx_data.get_layer_by_name("collision_layer"):
            if wall.name == "platform":
                self.wall_type.append("platform")
            else:
                self.wall_type.append("solid")
            self.walls.append(pygame.Rect(
                wall.x, wall.y,
                wall.width, wall.height))

        self.spawn_points = list()
        self.player_pos = [0, 0]

        for position in self.tmx_data.get_layer_by_name("spawn_point_layer"):
            if position.name == "player":
                self.player_pos = [position.x, position.y]
            else:
                self.spawn_points.append([position.x, position.y])

        # create new data source for pyscroll
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, surface.get_size())
        self.map_layer.zoom = 1

        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=0)

        #player.position = self.map_layer.map_rect.center
        self.spawn_zombies()
        #self.group.add(player)

    def draw(self, surface, player, time):

        # center the map/screen on our Hero
        self.group.center(player.rect.center)
        # draw the map and all sprites

        self.group.draw(surface)
        #"{0:.2f}".format(5)
        surface.blit(self.timer_font.render("{0:.2f}".format(time), 1, (0, 0, 0)), (20, 15))

    def spawn_zombies(self):
        for zombie in self.spawn_points:
            self.zombies.append(enemies.Zombie(self.dt, self.walls, self.map_size, zombie))
            self.group.add(self.zombies[-1])

    def add_sprites(self, sprites):
        for sprite in sprites:
            self.group.add(sprite)

    def remove_sprites(self, sprites):
        for sprite in sprites:
            self.group.remove(sprite)

    def add_animation(self, rects):
        for rect in rects:
            self.group.add(rect)

    def win_update(self, surface, score):
        if self.win_animation_counter % self.FPS == 0:
            screen_size = surface.get_size()
            position = random.randint(0, screen_size[0]), random.randint(0, screen_size[1])
            for block in range(30):
                self.win_animation_group.add(player.AnimationRect(position, (4, 4), self.dt))
        self.win_animation_counter += 1
        surface.blit(self.magneto_font.render("You win", 1, (0, 0, 0)), (100, 30))
        surface.blit(self.magneto_font.render("Your score is:", 1, (0, 0, 0)), (20, 100))
        surface.blit(self.magneto_font.render(str(int(score)), 1, (0, 0, 0)), (180, 170))
        self.win_animation_group.update()
        self.win_animation_group.draw(surface)

    def enter_score(self, surface, name):
        surface.fill((255, 255, 255))
        surface.blit(self.magneto_font.render("Enter your", 1, (0, 0, 0)), (70, 10))
        surface.blit(self.magneto_font.render("name", 1, (0, 0, 0)), (170, 100))
        pygame.draw.rect(surface, (0, 0, 0), (68, 180, self.magneto_font.size("AAAAA")[0], self.magneto_font.size("AAAAA")[1]), 2)
        surface.blit(self.magneto_font.render(name, 1, (0, 0, 0)), (70, 180))




class Menu(object):

    def __init__(self, surface):
        pygame.font.init()
        self.screen_size = surface.get_size()
        self.button_font = pygame.font.SysFont("magneto", 25)
        self.title_font = pygame.font.SysFont("magneto", 40)
        self.title = self.title_font.render("Zombie world", 1, (0, 0, 0))
        self.buttons = list()
        self.buttons.append(Button("Play", [20, 15], self.button_font, [self.screen_size[0], 50], (0, 0, 0), [0, 50]))
        self.buttons.append(Button("Leaderboard", [20, 15], self.button_font, [self.screen_size[0], 50], (0, 0, 0), [0, 115]))
        self.buttons.append(Button("Settings", [20, 15], self.button_font, [self.screen_size[0], 50], (0, 0, 0), [0, 180]))
        self.buttons.append(Button("Exit", [20, 15], self.button_font, [self.screen_size[0], 50], (0, 0, 0), [0, 245]))

    def update(self, surface):
        surface.fill((255, 255, 255))
        surface.blit(self.title, (100, 0))
        for button in self.buttons:
            surface.blit(button.image, (button.screen_pos[0], button.screen_pos[1]))

    def click(self, position):
        for button in self.buttons:
            if button.click(position):
                return button.text
        return False

    def display_leaderboard(self, surface, leaderboard, scroll_position):
        surface.fill((255, 255, 255))
        surface.blit(self.buttons[1].image, (0, 0))
        for position in range(5):
            try:
                surface.blit(self.button_font.render(leaderboard[position + scroll_position], 1, (0, 0, 0)), (25, (80 + (position * 40))))
            except IndexError:
                pass

    def display_settings(self, surface, switches, mouse_pos):
        surface.fill((255, 255, 255))
        surface.blit(self.buttons[2].image, (0, 0))

        for switch in switches:
            switch.update(mouse_pos)
            switch.draw(surface)


class Button(object):
    def __init__(self, text, text_pos, font, size, colour, screen_pos):
        self.screen_pos = screen_pos
        self.text = text
        self.image = pygame.Surface(size)
        self.image.fill(colour)
        if colour == (0, 0, 0):
            self.text_colour = (255, 255, 255)
        else:
            self.text_colour = (0, 0, 0)
        self.image.blit(font.render(text, 1, self.text_colour), (text_pos[0], text_pos[1]))
        self.rect = self.image.get_rect()
        self.rect.x = screen_pos[0]
        self.rect.y = screen_pos[1]

    def click(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False


class Switch(object):
    def __init__(self, position, dt):
        self.dt = dt
        self.back_position = [position[0], position[1]]
        self.front_position = [position[0], position[1]]
        self.collision_rect = pygame.Rect(position, (80, 30))
        self.back = pygame.Surface([80, 30])
        self.back.fill((255, 255, 255))
        pygame.draw.rect(self.back, (0, 0, 0), ((0, 0), (self.back.get_size())), 5)
        self.front = pygame.Surface([30, 30])
        self.front.fill((0, 0, 0))
        self.back_rect = self.back.get_rect()
        self.front_rect = self.front.get_rect()
        self.moving = False
        self.direction = True  # True is right, False is left
        self.velocity = 0
        self.acceleration = 300

    def draw(self, surface):
        surface.blit(self.back, self.back_position)
        surface.blit(self.front, self.front_position)

    def update(self, mouse_pos):
        if self.moving:
            self.velocity += self.acceleration * self.dt
            self.front_position[0] += self.velocity * self.dt
            if self.front_position[0] >= (self.back_position[0] + 50):
                self.front_position[0] = self.back_position[0] + 50
                self.moving = False
                self.acceleration *= -1
                self.direction = not self.direction
                self.velocity = 0
            if self.front_position[0] <= (self.back_position[0]):
                self.front_position[0] = self.back_position[0]
                self.moving = False
                self.acceleration *= -1
                self.direction = not self.direction
                self.velocity = 0
        elif self.collision_rect.collidepoint(mouse_pos):
            self.moving = True

    def check_state(self):
        return not self.direction


