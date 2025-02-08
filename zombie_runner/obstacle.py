import pygame as pg
import random

class Obstacle(pg.sprite.Sprite):
    def __init__(self, x, y, image_path, screen_width):
        super().__init__()
        self.image = pg.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.screen_width = screen_width

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()