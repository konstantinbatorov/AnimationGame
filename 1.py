import pygame

# Инициализация библиотеки Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512
FPS = 60  # Частота обновления кадров

# Параметры спрайтов
SPRITE_SIZE = 32  # Размер кадра спрайта в пикселях
ANIMATION_SPEED = 8  # Задержка между кадрами анимации

# Физические параметры
GRAVITY = 0.4  # Ускорение свободного падения
JUMP_POWER = -10  # Начальная скорость прыжка
WALK_SPEED = 2  # Скорость ходьбы
RUN_SPEED = 4   # Скорость бега


class Platform:
    """
    Класс платформы, на которой может стоять персонаж
    """
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)


class Hero:
    """
    Класс персонажа с системой анимации
    Управляет состояниями анимации и физикой персонажа
    """
    
    def __init__(self, x, y):
        """
        Инициализация персонажа
        Args:
            x, y: начальные координаты персонажа
        """
        # Позиция персонажа
        self.x = x
        self.y = y
        
        # Состояние анимации
        self.current_animation = "stance"  # Текущая анимация
        self.current_frame = 0  # Текущий кадр анимации
        self.animation_timer = 0  # Таймер смены кадров
        
        # Загрузка спрайт-листа
        self.sprite_sheet = pygame.image.load("hero_spritesheet.png").convert_alpha()
        
        # Конфигурация анимаций: (название, количество кадров)
        self.animations = [
            ("stance", 4),    # базовая стойка
            ("run", 8),       # бег
            ("walk", 8),      # ходьба
            ("jump", 6),      # прыжок
        ]
        
        # Хранилище кадров анимации
        self.animation_frames = {}
        
        # Физические параметры
        self.speed_y = 0  # Вертикальная скорость
        self.speed_x = 0  # Горизонтальная скорость
        self.facing_right = True  # Направление взгляда
        
        # Размеры персонажа (можно подогнать под спрайт)
        self.width = SPRITE_SIZE
        self.height = SPRITE_SIZE
        
        # Инициализация анимационных кадров
        self._load_all_animations()
    
    def _load_all_animations(self):
        """
        Загружает все кадры анимации из спрайт-листа
        Обрабатывает спрайт-лист последовательно слева направо, сверху вниз
        """
        sheet_width = self.sprite_sheet.get_width()
        frames_per_row = sheet_width // SPRITE_SIZE
        
        frame_number = 0
        
        for animation_name, frame_count in self.animations:
            frames = []
            for _ in range(frame_count):
                column = frame_number % frames_per_row
                row = frame_number // frames_per_row
                frame_rect = pygame.Rect(
                    column * SPRITE_SIZE,
                    row * SPRITE_SIZE,
                    SPRITE_SIZE,
                    SPRITE_SIZE
                )
                frame = self.sprite_sheet.subsurface(frame_rect)
                frames.append(frame)
                frame_number += 1
            self.animation_frames[animation_name] = frames
    
    def change_animation(self, new_animation):
        if (new_animation in self.animation_frames and new_animation != self.current_animation):
            self.current_animation = new_animation
            self.current_frame = 0
            self.animation_timer = 0
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, platforms):
        # Горизонтальное движение + коллизия по горизонтали
        self.x += self.speed_x
        hero_rect = self.get_rect()
        for platform in platforms:
            if hero_rect.colliderect(platform.rect):
                # Проверяем, находится ли персонаж "на уровне" платформы по вертикали
                # Если персонаж снизу платформы (его верхняя грань ниже нижней грани платформы), не сдвигаем
                if hero_rect.bottom <= platform.rect.top or hero_rect.top >= platform.rect.bottom:
                    # Персонаж под платформой или выше неё — игнорируем горизонтальную коллизию
                    continue
                if self.speed_x > 0:  # Движение вправо
                    self.x = platform.rect.left - self.width
                elif self.speed_x < 0:  # Движение влево
                    self.x = platform.rect.right
                hero_rect = self.get_rect()
        
        # Вертикальное движение и гравитация
        self.speed_y += GRAVITY
        self.y += self.speed_y
        hero_rect = self.get_rect()
        
        # Коллизия по вертикали
        collided_platform = None
        for platform in platforms:
            if hero_rect.colliderect(platform.rect):
                if self.speed_y > 0:  # Падение вниз
                    self.y = platform.rect.top - self.height
                    self.speed_y = 0
                    collided_platform = platform
                    hero_rect = self.get_rect()
                elif self.speed_y < 0:  # Подпрыгивание и удар о платформу сверху
                    self.y = platform.rect.bottom
                    self.speed_y = 0
                    hero_rect = self.get_rect()
        
        # Анимация
        self.animation_timer += 1
        if self.animation_timer >= ANIMATION_SPEED:
            frames_in_animation = len(self.animation_frames[self.current_animation])
            self.current_frame = (self.current_frame + 1) % frames_in_animation
            self.animation_timer = 0
        
        # Ограничение по горизонтали
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        
        # Возврат к базовой анимации, если не прыгаем и не двигаемся
        if self.speed_y == 0:
            if self.speed_x == 0:
                self.change_animation("stance")
            else:
                # Бег если скорость равна RUN_SPEED, иначе ходьба
                if abs(self.speed_x) == RUN_SPEED:
                    self.change_animation("run")
                else:
                    self.change_animation("walk")
        else:
            self.change_animation("jump")
    
    def draw(self, screen):
        current_image = self.animation_frames[self.current_animation][self.current_frame]
        if not self.facing_right:
            current_image = pygame.transform.flip(current_image, True, False)
        screen.blit(current_image, (self.x, self.y))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Анимированный герой с платформой")
    clock = pygame.time.Clock()
    
    platforms = [
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Земля
        Platform(0, 220, 64, 32),
        Platform(0, 270, 200, 25),
        Platform(250, 350, 100, 40),
        Platform(412, 400, 100, 30),
        Platform(100, 425, 50, 50),
    ]
    
    try:
        hero = Hero(SCREEN_WIDTH // 2 - SPRITE_SIZE // 2, SCREEN_HEIGHT - 40 - SPRITE_SIZE)
    except pygame.error:
        print("Ошибка: файл 'hero_spritesheet.png' не найден!")
        print("Поместите файл спрайт-листа в директорию с программой")
        return
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        
        hero.speed_x = 0
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = RUN_SPEED if is_running else WALK_SPEED
        
        if keys[pygame.K_a]:
            hero.speed_x = -speed
            hero.facing_right = False
        if keys[pygame.K_d]:
            hero.speed_x = speed
            hero.facing_right = True
        
        if keys[pygame.K_w] and hero.speed_y == 0:
            hero.speed_y = JUMP_POWER
        
        hero.update(platforms)
        
        screen.fill((30, 30, 60))
        for platform in platforms:
            platform.draw(screen)
        hero.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
