import pygame as pg

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pg.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.velocity = 0  # Скорость падения

    def update(self):
        # Симуляция падения (гравитация)
        self.velocity += 0.5  # Увеличиваем скорость падения
        self.rect.y += self.velocity

    def jump(self):
        # Подъем вверх
        self.velocity = -10  # Устанавливаем отрицательную скорость для прыжка