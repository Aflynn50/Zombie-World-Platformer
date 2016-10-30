import pygame
import sys
import time
import os
import math
import pytmx
import collision
import map
import player
from pygame.locals import *


class Zombie(pygame.sprite.Sprite):

    def __init__(self, dt, walls, map_size, pos):
        pygame.sprite.Sprite.__init__(self)
        self.dt = dt

        self.width = 32
        self.height = 32
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.old_rect = pygame.Rect(pos[0], pos[1], self.width, self.height)
        self.acceleration = -500
        self.zombie_position = pos
        self.velocity = list([0, 0])
        self.ZOMBIE_MOVE_SPEED = 65
        self.collision_list = []
        self.walls = walls
        self.animation_speed = 5
        self.time = time.clock() * self.animation_speed
        self.av = 5
        self.time_sin = 0
        self.animation_rect = pygame.Rect(self.av, self.av * 2, (self.width - (2 * self.av)), (self.height - self.av))
        self.map_size = map_size
        self.direction = False  # True is right, False is left

    def update(self):
        self.collision_list = []
        self.time = time.clock() * self.animation_speed
        self.time_sin = math.sin(self.time)

        if self.direction:
            self.velocity[0] = self.ZOMBIE_MOVE_SPEED + self.time_sin * 20
        else:
            self.velocity[0] = -self.ZOMBIE_MOVE_SPEED + self.time_sin * 20

        self.velocity[1] -= self.dt * self.acceleration
        self.zombie_position[0] += self.dt * self.velocity[0]
        self.zombie_position[1] += self.dt * self.velocity[1]
        self.rect.x = self.zombie_position[0]
        self.rect.y = self.zombie_position[1]

        for wall_num in range(len(self.walls)):
            if self.rect.colliderect(self.walls[wall_num]):
                self.collision_list.append(wall_num)

        for collision_wall_num in self.collision_list:
            if self.rect.x <= self.walls[collision_wall_num].right <= self.old_rect.x:
                self.zombie_position[0] = self.walls[collision_wall_num].right
                self.direction = True

            if self.rect.right >= self.walls[collision_wall_num].x >= self.old_rect.right:
                self.zombie_position[0] = self.walls[collision_wall_num].x - self.width
                self.direction = False

            if self.rect.bottom >= self.walls[collision_wall_num].y >= self.old_rect.bottom:
                self.velocity[1] = 0
                self.zombie_position[1] = self.walls[collision_wall_num].y - self.height

        if self.rect.right >= self.map_size[0]:
            self.zombie_position[0] = self.map_size[0] - self.width
            self.direction = False
        if self.rect.x <= 0:
            self.zombie_position[0] = 0
            self.direction = True

        self.rect.x = self.zombie_position[0]
        self.rect.y = self.zombie_position[1]
        if self.rect != self.old_rect:
            self.old_rect.x = self.rect.x
            self.old_rect.y = self.rect.y

        self.animation()

    #def load_zombie_tileset(self):
    #    for x in range(0, int(self.tileset_image_size[0] / self.tile_size[0])):
    #        self.zombie_tiles.append(list([]))
    #        for y in range(0, int(self.tileset_image_size[1] / self.tile_size[1])):
    #            rect = pygame.Rect((x * self.tile_size[0]), (y * self.tile_size[1]), self.tile_size[0], self.tile_size[1])
    #            self.zombie_tiles[x].append(self.tile_set.subsurface(rect))

    def animation(self):
        self.image.fill((255, 255, 255))
        self.animation_rect = pygame.Rect(self.av, self.av * 2, (self.width - (2 * self.av)), (self.height - self.av))

        self.animation_rect.x += self.time_sin * self.av
        self.animation_rect.w -= self.time_sin * self.av

        self.animation_rect.y -= self.time_sin * self.av
        self.animation_rect.h += self.time_sin * self.av

        self.image.fill((0, 0, 0), self.animation_rect)

        self.animation_rect.x += self.rect.x
        self.animation_rect.y += self.rect.y







