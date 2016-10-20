import pygame
import sys
import time
import os
import math
import enemies
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
        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.map_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        # setup level geometry with simple pygame rects, loaded from pytmx
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

    def draw(self, surface, player):

        # center the map/screen on our Hero
        self.group.center(player.rect.center)
        # draw the map and all sprites

        self.group.draw(surface)

    def spawn_zombies(self):
        for zombie in self.spawn_points:
            self.zombies.append(enemies.Zombie(self.dt, self.walls, self.map_size, zombie))
            self.group.add(self.zombies[-1])

    def add_sprites(self, sprites):
        for sprite in sprites:
            self.group.add(sprite)


class Menu(object):

    def __init__(self, surface):
        pygame.font.init()
        self.screen_size = surface.get_size()
        self.button_font = pygame.font.SysFont("magneto", 25)
        self.title_font = pygame.font.SysFont("magneto", 40)
        self.play_button = pygame.Surface([self.screen_size[0], 50])
        self.play_button.fill((0, 0, 0))
        self.play_button.blit(self.button_font.render("Play", 1, (255, 255, 255)), (20, 15))
        self.title = self.title_font.render("Zombie world", 1, (0, 0, 0))
        self.play_rect = self.play_button.get_rect()
        self.play_rect.x = 0
        self.play_rect.y = 100

    def update(self, surface):
        surface.fill((255, 255, 255))
        surface.blit(self.play_button, (0, 100))
        surface.blit(self.title, (100, 0))

    def click(self, position):
        if self.play_rect.collidepoint(position):
            return True
        return False







