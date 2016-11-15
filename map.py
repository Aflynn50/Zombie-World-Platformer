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
        "{0:.2f}".format(5)
        surface.blit(self.timer_font.render("{0:.1f}".format(time), 1, (0, 0, 0)), (20, 15))

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
        self.play_button = pygame.Surface([self.screen_size[0], 50])
        self.exit_button = pygame.Surface([self.screen_size[0], 50])
        self.leader_button = pygame.Surface([self.screen_size[0], 50])
        self.settings_button = pygame.Surface([self.screen_size[0], 50])
        self.play_button.fill((0, 0, 0))
        self.exit_button.fill((0, 0, 0))
        self.leader_button.fill((0, 0, 0))
        self.settings_button.fill((0, 0, 0))
        self.play_button.blit(self.button_font.render("Play", 1, (255, 255, 255)), (20, 15))
        self.exit_button.blit(self.button_font.render("Exit", 1, (255, 255, 255)), (20, 15))
        self.leader_button.blit(self.button_font.render("Leaderboard", 1, (255, 255, 255)), (20, 15))
        self.settings_button.blit(self.button_font.render("Settings", 1, (255, 255, 255)), (20, 15))
        self.title = self.title_font.render("Zombie world", 1, (0, 0, 0))
        self.play_rect = self.play_button.get_rect()
        self.exit_rect = self.exit_button.get_rect()
        self.leader_rect = self.leader_button.get_rect()
        self.settings_rect = self.settings_button.get_rect()
        self.play_rect.x = 0
        self.play_rect.y = 50
        self.leader_rect.x = 0
        self.leader_rect.y = 115
        self.settings_rect.x = 0
        self.settings_rect.y = 180
        self.exit_rect.x = 0
        self.exit_rect.y = 245

    def update(self, surface):
        surface.fill((255, 255, 255))
        surface.blit(self.play_button, (0, 50))
        surface.blit(self.exit_button, (0, 245))
        surface.blit(self.leader_button, (0, 115))
        surface.blit(self.settings_button, (0, 180))
        surface.blit(self.title, (100, 0))

    def click(self, position):
        if self.play_rect.collidepoint(position):
            return "play"
        elif self.exit_rect.collidepoint(position):
            return "exit"
        elif self.leader_rect.collidepoint(position):
            return "leader"
        elif self.settings_rect.collidepoint(position):
            return "settings"
        return False

    def display_leaderboard(self, surface, leaderboard, scroll_position):
        surface.fill((255, 255, 255))
        surface.blit(self.leader_button, (0, 0))
        for position in range(5):
            try:
                surface.blit(self.button_font.render(leaderboard[position + scroll_position], 1, (0, 0, 0)), (25, (80 + (position * 40))))
            except IndexError:
                pass










