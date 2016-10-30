import pygame
import sys
import time
import os
import math
import random
from pygame.locals import *


class Player(pygame.sprite.Sprite):

    def __init__(self, dt, pos, map_size, walls, wall_type):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(os.path.join("resources/sprites/player.png"))
        self.dt = dt
        self.width = 32
        self.height = 32
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.image.fill((0, 0, 0))
        self.player_position = pos
        self.rect = self.image.get_rect()
        self.rect.x = self.player_position[0]
        self.rect.y = self.player_position[1]
        self.old_rect = pygame.Rect(0, 0, self.width, self.height)
        self.player_position = pos
        self.velocity = list([0, 0])
        self.acceleration = -500
        self.PLAYER_MOVE_SPEED = 200
        self.PLAYER_JUMP_SPEED = 300
        self.animation_speed = 5
        self.trans_colour = (236, 153, 46)
        self.image.set_colorkey(self.trans_colour)
        self.time = time.clock() * self.animation_speed
        self.av = 10
        self.death_animation_rects = list()
        self.left = False
        self.right = False
        self.up = False
        self.jumping = True
        self.collision = False
        self.collision_list = []
        self.walls = walls
        self.wall_type = wall_type
        self.map_width = map_size[0]
        self.map_height = map_size[1]

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
        self.player_position[0] += self.dt * self.velocity[0]
        self.player_position[1] += self.dt * self.velocity[1]
        self.rect.x = self.player_position[0]
        self.rect.y = self.player_position[1]

        self.jumping = True

        for wall_num in range(len(self.walls)):
            if self.rect.colliderect(self.walls[wall_num]):
                self.collision_list.append(wall_num)

        for collision_wall_num in self.collision_list:
            if self.rect.x <= self.walls[collision_wall_num].right <= self.old_rect.x and self.wall_type[
                    collision_wall_num] == "solid":
                self.player_position[0] = self.walls[collision_wall_num].right

            if self.rect.right >= self.walls[collision_wall_num].x >= self.old_rect.right and self.wall_type[
                    collision_wall_num] == "solid":
                self.player_position[0] = self.walls[collision_wall_num].x - self.width

            if self.rect.bottom >= self.walls[collision_wall_num].y >= self.old_rect.bottom:
                self.velocity[1] = 0
                self.player_position[1] = self.walls[collision_wall_num].y - self.height
                self.jumping = False

        if self.rect.x >= self.map_width:
            return "win"

        if self.rect.x <= 0:
            self.player_position[0] = 0

        if self.rect.y >= self.map_height:
            return "lose"

        self.rect.x = self.player_position[0]
        self.rect.y = self.player_position[1]
        if self.rect != self.old_rect:
            self.old_rect.x = self.rect.x
            self.old_rect.y = self.rect.y
        return "carry on"

    def death_animation_init_(self):
        for x in range(0, self.width, int(self.width / 4)):
            for y in range(0, self.height, int(self.height / 4)):
                width = int(self.rect.w / 4)
                height = int(self.rect.h / 4)
                self.death_animation_rects.append(AnimationRect((self.rect.x + x, self.rect.y + y), (width, height), self.dt))
        return self.death_animation_rects

    def death_animation_update(self, surface):
        for rect in self.death_animation_rects:
            rect.update(surface)


class AnimationRect(pygame.sprite.Sprite):
    def __init__(self, position, size, dt):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size[0], size[1]])
        self.image.fill((0, 0, 0))
        self.dt = dt
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.rect_position = list(position)
        self.velocity = list([(75 - random.randint(0, 150)), (random.randint(200, 300) * -1)])
        self.acceleration = -500

    def update(self, surface):
        self.velocity[1] -= self.dt * self.acceleration
        self.rect_position[0] += self.dt * self.velocity[0]
        self.rect_position[1] += self.dt * self.velocity[1]
        self.rect.x = self.rect_position[0]
        self.rect.y = self.rect_position[1]
        if self.rect.y >= 1000:
            self.kill()




