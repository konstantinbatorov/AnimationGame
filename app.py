import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512
FPS = 60

# Параметры спрайтов
SPRITE_SIZE = 32
ANIMATION_SPEED = 8

# Физические параметры
GRAVITY = 0.4
JUMP_POWER = -10
WALK_SPEED = 2
RUN_SPEED = 4


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)


class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.current_animation = "stance"
        self.current_frame = 0
        self.animation_timer = 0

        # Загрузка спрайт-листа
        try:
            self.sprite_sheet = pygame.image.load("characters.png").convert_alpha()
        except pygame.error:
            raise pygame.error("Файл 'characters.png' не найден!")

        # Анимации (название, количество кадров)
        # Используем расширенный набор из второго кода
        self.animations = [
            ("stance", 4),
            ("run", 4),
            ("walk", 4),
            ("jump", 4),
            ("hit", 2),
            ("slash", 3),
            ("punch", 1),
            ("climb", 4),
            ("back", 1)
        ]

        # Хранилище кадров анимации
        self.animation_frames = {}

        # Физика
        self.speed_y = 0
        self.speed_x = 0
        self.facing_right = True

        self.width = SPRITE_SIZE
        self.height = SPRITE_SIZE

        # Для коллизий
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Начинаем с "stance"
        self.change_animation("stance")

        # Индекс первого кадра в спрайт-листе (как во втором коде)
        self.first_frame_index = 23

        self._load_all_animations()

    def _load_all_animations(self):
        sheet_width = self.sprite_sheet.get_width()
        frames_per_row = sheet_width // SPRITE_SIZE

        frame_number = self.first_frame_index

        for animation_name, frame_count in self.animations:
            frames = []
            for _ in range(frame_count):
                col = frame_number % frames_per_row
                row = frame_number // frames_per_row
                rect = pygame.Rect(col * SPRITE_SIZE, row * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
                frame = self.sprite_sheet.subsurface(rect)
                frames.append(frame)
                frame_number += 1
            self.animation_frames[animation_name] = frames

    def change_animation(self, new_animation):
        if new_animation in self.animation_frames and new_animation != self.current_animation:
            self.current_animation = new_animation
            self.current_frame = 0
            self.animation_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, platforms):
        # Горизонтальное движение + коллизии
        self.x += self.speed_x
        hero_rect = self.get_rect()
        for platform in platforms:
            if hero_rect.colliderect(platform.rect):
                # Проверяем вертикальное положение для игнорирования горизонтальной коллизии
                if hero_rect.bottom <= platform.rect.top or hero_rect.top >= platform.rect.bottom:
                    continue
                if self.speed_x > 0:
                    self.x = platform.rect.left - self.width
                elif self.speed_x < 0:
                    self.x = platform.rect.right
                hero_rect = self.get_rect()

        # Вертикальное движение и гравитация
        self.speed_y += GRAVITY
        self.y += self.speed_y
        hero_rect = self.get_rect()

        collided_platform = None
        for platform in platforms:
            if hero_rect.colliderect(platform.rect):
                if self.speed_y > 0:
                    self.y = platform.rect.top - self.height
                    self.speed_y = 0
                    collided_platform = platform
                    hero_rect = self.get_rect()
                elif self.speed_y < 0:
                    self.y = platform.rect.bottom
                    self.speed_y = 0
                    hero_rect = self.get_rect()

        # Ограничение по горизонтали
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

        # Обновляем rect для коллизий
        self.rect.topleft = (self.x, self.y)

        # Анимация
        self.animation_timer += 1
        if self.animation_timer >= ANIMATION_SPEED:
            frames_count = len(self.animation_frames[self.current_animation])
            self.current_frame = (self.current_frame + 1) % frames_count
            self.animation_timer = 0

        # Выбор анимации по состоянию
        if self.speed_y == 0:
            if self.speed_x == 0:
                self.change_animation("stance")
            else:
                if abs(self.speed_x) == RUN_SPEED:
                    self.change_animation("run")
                else:
                    self.change_animation("walk")
        else:
            self.change_animation("jump")

    def draw(self, screen):
        image = self.animation_frames[self.current_animation][self.current_frame]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, (self.x, self.y))


# Частицы и источник частиц из второго кода

particles = []
source = {
    'x': SCREEN_WIDTH - 128,
    'y': 128,
    'timer': 0,
    'radius': 30
}

def create_particles(count=5):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        particle = {
            'x': source['x'],
            'y': source['y'],
            'speed_x': math.cos(angle) * speed,
            'speed_y': math.sin(angle) * speed,
            'life': random.randint(40, 100),
            'color': [
                random.randint(200, 255),
                random.randint(100, 200),
                random.randint(0, 50)
            ],
            'size': random.randint(3, 8)
        }
        particles.append(particle)

def update_particles():
    global particles
    for particle in particles[:]:
        particle['x'] += particle['speed_x']
        particle['y'] += particle['speed_y']

        particle['speed_x'] *= 0.98
        particle['speed_y'] *= 0.98

        particle['speed_y'] += 0.1

        particle['life'] -= 1
        particle['size'] = max(1, particle['size'] * 0.97)

        if particle['life'] <= 0 or particle['size'] < 0.5:
            particles.remove(particle)

def draw_particles(screen):
    for particle in particles:
        pygame.draw.circle(
            screen,
            particle['color'],
            (int(particle['x']), int(particle['y'])),
            int(particle['size'])
        )

def draw_source(screen):
    source['timer'] += 0.05
    pulse = math.sin(source['timer']) * 0.2 + 1
    current_radius = int(source['radius'] * pulse)

    pygame.draw.circle(screen, (255, 255, 0), (source['x'], source['y']), current_radius)

    glow = pygame.Surface((current_radius*4, current_radius*4), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 200, 0, 50), (current_radius*2, current_radius*2), current_radius*2)
    screen.blit(glow, (source['x'] - current_radius*2, source['y'] - current_radius*2))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Анимированный герой с платформами и частицами")
    clock = pygame.time.Clock()

    # Платформы из первого кода
    platforms = [
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
        Platform(0, 220, 64, 32),
        Platform(0, 270, 200, 25),
        Platform(250, 350, 100, 40),
        Platform(412, 400, 100, 30),
        Platform(100, 425, 50, 50),
    ]

    try:
        hero = Hero(SCREEN_WIDTH // 2 - SPRITE_SIZE // 2, SCREEN_HEIGHT - 40 - SPRITE_SIZE)
    except pygame.error as e:
        print(e)
        print("Поместите файл 'characters.png' в директорию с программой")
        return

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
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

        # Обновление и отрисовка частиц
        create_particles()
        update_particles()

        screen.fill((86, 193, 168))

        for platform in platforms:
            platform.draw(screen)

        draw_particles(screen)
        draw_source(screen)

        hero.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
