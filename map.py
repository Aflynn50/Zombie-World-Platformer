import pygame
import sys
import time
import os
import math
from pytmx import *
from pytmx.util_pygame import load_pygame
from pygame.locals import *
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup


class TiledRenderer(object):

    def __init__(self, filename, surface, player):
        tm = load_pygame(filename)

        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.pixel_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        # setup level geometry with simple pygame rects, loaded from pytmx
        self.walls = list()

        for wall in self.tmx_data.get_layer_by_name("collision_layer"):
            self.walls.append(pygame.Rect(
                wall.x, wall.y,
                wall.width, wall.height))

        self.spawn_points = list()
        self.player_pos = [0, 0]

        #for position in self.tmx_data.get_layer_by_name("spawn_point_layer"):
        #    if position.name == "player":
        #        self.player_pos = [position.x, position.y]
        #    else:
        #        self.spawn_points.append([position.x, position.y])

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

        player.position = self.map_layer.map_rect.center

        self.group.add(player)

    def draw(self, surface, player):

        # center the map/screen on our Hero
        self.group.center(player.rect.center)

        # draw the map and all sprites

        self.group.draw(surface)