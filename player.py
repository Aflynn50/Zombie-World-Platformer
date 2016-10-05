import pygame
import sys
import time
import os
import math
from pygame.locals import *


class Player(pygame.sprite.Sprite):

    def __init__(self, dt):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(os.path.join("resources/sprites/player.png"))
        self.dt = dt
        self.width = 32
        self.height = 64
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.velocity = list([0, 0])
        self.acceleration = -350
        self.rect = self.image.get_rect()
        self.old_rect = pygame.Rect(0, 0, self.width, self.height)
        self.PLAYER_MOVE_SPEED = 200
        self.PLAYER_JUMP_SPEED = 300
        self.left = False
        self.right = False
        self.up = False
        self.jumping = True
        self.collision = False
        self.collision_list = []
        self.walls = list()
        self.map_height = 0
        self.map_width = 0
        #pygame.key.set_repeat(int(1000 * self.dt), int(1000 * self.dt))

    def update(self, keys):
        self.left = False
        self.right = False
        self.up = False
        self.collision = False
        self.collision_list = []

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.right = True
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.left = True
        if keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.up = True

        if self.right:
            self.velocity[0] = self.PLAYER_MOVE_SPEED
        elif self.left:
            self.velocity[0] = -self.PLAYER_MOVE_SPEED
        elif not self.right or not self.left:
            self.velocity[0] = 0

        if self.up and not self.jumping:
            self.velocity[1] = -self.PLAYER_JUMP_SPEED
            self.jumping = True

        self.velocity[1] -= self.dt * self.acceleration
        self.rect.x += self.dt * self.velocity[0]
        self.rect.y += self.dt * self.velocity[1]

        for wall_num in range(len(self.walls)):
            if self.rect.colliderect(self.walls[wall_num]):
                self.collision_list.append(wall_num)


        for collision_wall_num in self.collision_list:
            if (self.rect.x <= self.walls[collision_wall_num].right <= self.old_rect.x) or (
                    self.rect.right >= self.walls[collision_wall_num].x >= self.old_rect.right):
                self.rect.x = self.old_rect.x

            if self.rect.bottom >= self.walls[collision_wall_num].y >= self.old_rect.bottom:
                self.velocity[1] = 0
                self.rect.y = self.old_rect.y
                self.jumping = False

        if self.rect.right >= self.map_width or self.rect.x <= 0:
            self.rect.x = self.old_rect.x

        if self.rect.bottom >= self.map_height:
            self.rect.y = self.old_rect.y

        self.old_rect.y = self.rect.y
        self.old_rect.x = self.rect.x

        #if self.collision_list > -1:
        #    self.jumping = False
        #    self.rect = self.old_rect
        #    self.collision = True

