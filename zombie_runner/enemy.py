import pygame as pg
import random

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, image_path, screen_width, screen_height):
        super().__init__()
        self.image = pg.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 2  # Скорость движения врага
        self.direction = 1  # 1 = вниз, -1 = вверх

    def update(self):
        # Движение по вертикали
        self.rect.y += self.speed * self.direction

        # Изменение направления при достижении границ
        if self.rect.top < self.screen_height // 4:
            self.direction = 1
        elif self.rect.bottom > self.screen_height * 3 // 4:
            self.direction = -1

