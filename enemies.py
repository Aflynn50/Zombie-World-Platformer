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
        #self.image = pygame.image.load(os.path.join("resources/sprites/player.png"))
        self.dt = dt
        self.width = 32
        self.height = 64
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        print(pos[0])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.old_rect = pygame.Rect(pos[0], pos[1], self.width, self.height)
        self.acceleration = -500
        self.velocity = list([0, 0])
        self.ZOMBIE_MOVE_SPEED = 100
        self.collision_list = []
        self.walls = walls
        self.map_size = map_size
        self.direction = True  # True is right, False is left

    def update(self):
        self.collision_list = []

        if self.direction:
            self.velocity[0] = self.ZOMBIE_MOVE_SPEED
        else:
            self.velocity[0] = -self.ZOMBIE_MOVE_SPEED

        self.velocity[1] -= self.dt * self.acceleration
        self.rect.x += self.dt * self.velocity[0]
        self.rect.y += self.dt * self.velocity[1]

        for wall_num in range(len(self.walls)):
            if self.rect.colliderect(self.walls[wall_num]):
                self.collision_list.append(wall_num)

        for collision_wall_num in self.collision_list:
            if self.rect.x <= self.walls[collision_wall_num].right <= self.old_rect.x:
                self.rect.x = self.walls[collision_wall_num].right
                self.direction = True

            if self.rect.right >= self.walls[collision_wall_num].x >= self.old_rect.right:
                self.rect.right = self.walls[collision_wall_num].x
                self.direction = False

            if self.rect.bottom >= self.walls[collision_wall_num].y >= self.old_rect.bottom:
                self.velocity[1] = 0
                self.rect.bottom = self.walls[collision_wall_num].y

        if self.rect.right >= self.map_size[0]:
            self.rect.right = self.map_size[0]
            self.direction = False
        if self.rect.x <= 0:
            self.rect.x = 0
            self.direction = True

        self.old_rect.y = self.rect.y
        self.old_rect.x = self.rect.x



