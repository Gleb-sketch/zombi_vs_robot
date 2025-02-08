import pygame as pg
import random
import sys
from database import Database
from player import Player
from enemy import Enemy
from obstacle import Obstacle
import pygame_gui

class Game:
    def __init__(self):
        pg.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("Zombie Runner")
        self.clock = pg.time.Clock()
        self.db = Database()
        self.best_score = self.db.get_best_score()
        self.score = 0
        self.level = 1
        self.font = pg.font.Font(None, 36)
        self.running = True

        # Загрузка ресурсов
        try:
            self.player_image = "assets/images/zombie.png"
            self.enemy_image = "assets/images/robot.png"
            self.obstacle_image = "assets/images/fire.png"
            self.background_image = pg.transform.scale(pg.image.load("assets/images/background.png").convert(), (self.screen_width, self.screen_height))  # Масштабируем изображение
            pg.mixer.music.load("assets/audio/music.mp3")
            self.hit_sound = pg.mixer.Sound("assets/audio/hit.wav")
            # Загрузка изображений для стартового и финального экранов
            self.start_screen_image = pg.image.load("assets/images/start_screen.png").convert()
            self.game_over_screen_image = pg.image.load("assets/images/game_over_screen.png").convert()

        except FileNotFoundError as e:
            print(f"Не найден файл: {e}")
            pg.quit()
            sys.exit()

        self.player = Player(50, self.screen_height // 2, self.player_image)
        self.enemy = Enemy(self.screen_width - 50, self.screen_height // 2, self.enemy_image, self.screen_width, self.screen_height)

        self.obstacles = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemy)

        self.enemy_shoot_timer = 0
        self.enemy_shoot_interval = 2000
        self.game_state = "start_screen" # Начальное состояние - стартовый экран

        # Инициализация UI
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height), "assets/theme.json")
        self.exit_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((self.screen_width - 120, 1), (120, 40)),
                                                    text='Выход',
                                                    manager=self.ui_manager)

    def run(self):
        pg.mixer.music.play(-1)

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

        pg.mixer.music.stop()
        self.db.close()
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.exit_button:
                        self.running = False # Завершаем игру при нажатии на кнопку "Выход"
            self.ui_manager.process_events(event)
            if self.game_state == "start_screen":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.game_state = "playing"
            elif self.game_state == "playing":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.player.jump()
            elif self.game_state == "game_over_screen":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.reset()
                        self.game_state = "playing"

    def update(self):
        time_delta = self.clock.get_time() / 1000.0
        self.ui_manager.update(time_delta)
        if self.game_state == "playing":
            self.player.update()
            self.enemy.update()

            # Не даем врагу выйти за границы экрана
            if self.enemy.rect.top < 0:
                self.enemy.direction = 1
            if self.enemy.rect.bottom > self.screen_height:
                self.enemy.direction = -1

            for obstacle in self.obstacles:
               obstacle.update()
               if pg.sprite.collide_rect(self.player, obstacle):
                 self.hit_sound.play()
                 self.game_over()
                 return # Важно выйти из update(), чтобы избежать двойных вызо

               if obstacle.rect.right < 0:
                 self.obstacles.remove(obstacle)
                 self.all_sprites.remove(obstacle)

            self.enemy_shoot_timer += self.clock.get_time()
            if self.enemy_shoot_timer > self.enemy_shoot_interval:
                 self.shoot_obstacle()
                 self.enemy_shoot_timer = 0

            # Условие Game Over - столкновение с верхней или нижней границей
            if self.player.rect.top < 0 or self.player.rect.bottom > self.screen_height:
              self.game_over()
              return # Важно выйти из update(), чтобы избежать двойных вызовов

            self.score += 1
            if self.score % 500 == 0:
              self.level += 1
              self.enemy_shoot_interval = max(500, self.enemy_shoot_interval - 100)

    def shoot_obstacle(self):
        # Создаем и добавляем препятствие
        obstacle = Obstacle(self.enemy.rect.x, self.enemy.rect.centery, self.obstacle_image, self.screen_width)
        self.obstacles.add(obstacle)
        self.all_sprites.add(obstacle)

    def draw(self):
        white_color = (255, 255, 255)  # Белый цвет
        if self.game_state == "start_screen":
            self.screen.blit(self.start_screen_image, (0, 0))
            text = self.font.render("Чтобы играть нажмите пробел. Удачи! Она вам понадобится))", True, white_color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))  # Размещаем внизу
            self.screen.blit(text, text_rect)

        elif self.game_state == "playing":
            self.screen.blit(self.background_image, (0, 0))
            self.all_sprites.draw(self.screen)

            # Отображение текста
            score_text = self.font.render(f"Score: {self.score}", True, white_color)
            level_text = self.font.render(f"Level: {self.level}", True, white_color)
            best_score_text = self.font.render(f"Top Score: {self.best_score}", True, white_color)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 40))
            self.screen.blit(best_score_text, (10, 70))
        elif self.game_state == "game_over_screen":
            self.screen.blit(self.game_over_screen_image, (0, 0))
            text = self.font.render("ХА-ХА-ХА! Вы проиграли! Для начала игры нажмите на пробел.  ", True, white_color )
            text_rect = text.get_rect(center=(self.screen_width // 2, 50))  # Размещаем вверху
            self.screen.blit(text, text_rect)

        self.ui_manager.draw_ui(self.screen)
        pg.display.flip()

    def game_over(self):
        pg.mixer.music.stop()
        if self.score > self.best_score:
            self.db.insert_score(self.score)
            self.best_score = self.score

        self.game_state = "game_over_screen"

    def reset(self):
        # Сброс параметров игры для начала новой игры
        self.score = 0
        self.level = 1
        self.player.rect.y = self.screen_height // 2
        self.player.velocity = 0 # Сбрасываем скорость падения
        self.enemy_shoot_interval = 2000

        for obstacle in self.obstacles:
            self.all_sprites.remove(obstacle) # Удаляем из all_sprites
        self.obstacles.empty()
        pg.mixer.music.play(-1)
        self.running = True
        self.game_state = "playing" # Устанавливаем состояние "playing" для продолжения игры

if __name__ == "__main__":
    game = Game()
    game.run()