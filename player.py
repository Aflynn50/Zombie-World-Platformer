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
        self.image = pygame.Surface([32, 64])
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.velocity = list([0, 0])
        self.acceleration = -200
        self.rect = self.image.get_rect()
        self.PLAYER_MOVE_SPEED = 200

    def update(self):
        for event in pygame.event.get():  # event handling loop
            if event.type == KEYDOWN and (event.key == K_d or event.key == K_RIGHT):
                self.velocity[0] = self.PLAYER_MOVE_SPEED
            elif event.type == KEYDOWN and (event.key == K_a or event.key == K_LEFT):
                self.velocity[0] = -self.PLAYER_MOVE_SPEED
            else:
                self.velocity[0] = 0
            if event.type == KEYDOWN and (event.key == K_w or event.key == K_UP):
                self.velocity[1] = -self.PLAYER_MOVE_SPEED
        self.velocity[1] -= self.dt * self.acceleration
        self.rect.x += self.dt * self.velocity[0]
        self.rect.y += self.dt * self.velocity[1]


