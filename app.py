from pygame import *
import random 
import math
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
        self.current_animation = "walk"  # Текущая анимация
        self.current_frame = 0  # Текущий кадр анимации
        self.animation_timer = 0  # Таймер смены кадров
        
        # Загрузка спрайт-листа
        self.sprite_sheet = image.load("characters.png").convert_alpha()
        
        # Конфигурация анимаций: (название, количество кадров)
        # self.animations = [
        #     ("stance", 4),    # базовая стойка
        #     ("run", 8),       # бег
        #     ("swing", 4),     # атака мечом
        #     ("block", 2),     # защита
        #     ("hit_die", 6),   # получение урона
        #     ("cast", 4),      # применение магии
        #     ("shoot", 4),     # дальняя атака
        #     ("walk", 8),      # ходьба
        #     ("duck", 2),      # приседание
        #     ("jump", 6),      # прыжок
        #     ("stairs_up", 8), # движение вверх по лестнице
        #     ("stairs_down", 8), # движение вниз по лестнице
        #     ("stand", 1),     # статичная поза
        # ]

        self.animations = [
            ('walk', 4),
            ('jump', 4),
            ('hit', 2),
            ('slash', 3),
            ('punch', 1),
            ('run', 4),
            ('climb', 4),
            ('back', 1)
        ]
        
        # Хранилище кадров анимации
        self.animation_frames = {}
        
        # Физические параметры
        self.speed_y = 0  # Вертикальная скорость
        self.ground_level = y  # Уровень поверхности
        self.facing_right = True  # Направление взгляда
        
        # Инициализация анимационных кадров
        self._load_all_animations()
    
    def _load_all_animations(self):
        """
        Загружает все кадры анимации из спрайт-листа
        Обрабатывает спрайт-лист последовательно слева направо, сверху вниз
        """
        # Параметры спрайт-листа
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        
        # Количество кадров в строке
        frames_per_row = sheet_width // SPRITE_SIZE
        
        frame_number = 23  # Индекс текущего кадра
        
        # Обработка каждой анимации
        for animation_name, frame_count in self.animations:
            frames = []  # Список кадров текущей анимации
            
            # Извлечение кадров
            for _ in range(frame_count):
                # Вычисление позиции кадра в сетке
                column = frame_number % frames_per_row
                row = frame_number // frames_per_row
                
                # Определение области кадра
                frame_rect = Rect(
                    column * SPRITE_SIZE,
                    row * SPRITE_SIZE,
                    SPRITE_SIZE,
                    SPRITE_SIZE
                )
                
                # Извлечение кадра из спрайт-листа
                frame = self.sprite_sheet.subsurface(frame_rect)
                frames.append(frame)
                frame_number += 1
            
            # Сохранение кадров анимации
            self.animation_frames[animation_name] = frames
    
    def change_animation(self, new_animation):
        """
        Изменяет текущую анимацию персонажа
        Args:
            new_animation: название новой анимации
        """
        # Проверка валидности и необходимости смены анимации
        if (new_animation in self.animation_frames and 
            new_animation != self.current_animation):
            self.current_animation = new_animation
            self.current_frame = 0  # Сброс к первому кадру
            self.animation_timer = 0  # Сброс таймера
    
    def update(self):
        """
        Обновление состояния персонажа
        Обрабатывает физику и анимацию
        """
        # Физическое моделирование
        self.speed_y += GRAVITY
        self.y += self.speed_y
        
        # Обработка столкновения с поверхностью
        if self.y >= self.ground_level:
            self.y = self.ground_level
            self.speed_y = 0
            
            # Возврат к базовой анимации после приземления
            if self.current_animation == "jump":
                self.change_animation("punch")
        
        # Обновление анимации
        self.animation_timer += 1
        
        # Смена кадра анимации
        if self.animation_timer >= ANIMATION_SPEED:
            frames_in_animation = len(self.animation_frames[self.current_animation])
            self.current_frame = (self.current_frame + 1) % frames_in_animation
            self.animation_timer = 0
    
    def draw(self, screen):
        """
        Отрисовка персонажа на экране
        Args:
            screen: поверхность для отрисовки
        """
        # Получение текущего кадра
        current_image = self.animation_frames[self.current_animation][self.current_frame]
        
        # Отражение спрайта при движении влево
        if not self.facing_right:
            current_image = transform.flip(current_image, True, False)
        
        # Отрисовка спрайта
        screen.blit(current_image, (self.x, self.y))

"""
Основная функция приложения
Содержит игровой цикл и обработку событий
"""
# Инициализация окна
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption("Анимированный герой")

# Инициализация таймера
clock = time.Clock()

# Создание экземпляра персонажа
try:
    hero = Hero(SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 32)
except error:
    print("Ошибка: файл 'characters.png' не найден!")
    print("Поместите файл спрайт-листа в директорию с программой")
    


particles = []
source = {
    'x': SCREEN_WIDTH - 128,      # X-координата центра
    'y': 128,      # Y-координата центра
    'timer': 0,    # Таймер для анимации пульсации
    'radius': 30   # Базовый радиус круга
}

def create_particles(count=5):
    """
    Создает новые частицы, исходящие из центра источника
    Args:
        count: int - количество создаваемых частиц (по умолчанию 5)
    Возвращает:
        None (но модифицирует глобальный список particles)
    """
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)  # Случайный угол вылета
        speed = random.uniform(2, 6)           # Случайная скорость
        
        # Создаем словарь с параметрами частицы
        particle = {
            'x': source['x'],                  # Начальная позиция X
            'y': source['y'],                  # Начальная позиция Y
            'speed_x': math.cos(angle) * speed, # Горизонтальная скорость
            'speed_y': math.sin(angle) * speed, # Вертикальная скорость
            'life': random.randint(40, 100),   # Время жизни (в кадрах)
            'color': [                         # Цвет (RGB)
                random.randint(200, 255),      # Красный (желто-оранжевый)
                random.randint(100, 200),      # Зеленый
                random.randint(0, 50)          # Синий (почти отсутствует)
            ],
            'size': random.randint(3, 8)       # Начальный размер
        }
        particles.append(particle)

def update_particles():
    """
    Обновляет состояние всех частиц (движение, жизнь, размер)
    Args:
        None
    Возвращает:
        None (но модифицирует глобальный список particles)
    """
    global particles
    for particle in particles[:]:  # Работаем с копией списка для безопасного удаления
        # Физика движения
        particle['x'] += particle['speed_x']
        particle['y'] += particle['speed_y']
        
        # Замедление частиц (эффект трения)
        particle['speed_x'] *= 0.98
        particle['speed_y'] *= 0.98
        
        # Гравитация (притяжение вниз)
        particle['speed_y'] += 0.1
        
        # Уменьшение времени жизни
        particle['life'] -= 1
        
        # Уменьшение размера с течением времени
        particle['size'] = max(1, particle['size'] * 0.97)
        
        # Удаление частиц, когда их жизнь закончилась или размер слишком мал
        if particle['life'] <= 0 or particle['size'] < 0.5:
            particles.remove(particle)

def draw_particles():
    """
    Отрисовывает все активные частицы на экране
    Args:
        None
    Возвращает:
        None (рисует на глобальной поверхности screen)
    """
    for particle in particles:
        draw.circle(
            screen,                      # Поверхность для рисования
            particle['color'],           # Цвет частицы
            (int(particle['x']), int(particle['y'])),  # Позиция
            int(particle['size'])        # Размер
        )

def draw_source():
    """
    Рисует центральный источник частиц (пульсирующий желтый круг)
    Args:
        None
    Возвращает:
        None (рисует на глобальной поверхности screen)
    """
    # Анимация пульсации
    source['timer'] += 0.05
    pulse = math.sin(source['timer']) * 0.2 + 1  # Пульсация от 0.8 до 1.2
    current_radius = int(source['radius'] * pulse)
    
    # Рисуем ядро источника
    draw.circle(
        screen,
        (255, 255, 0),                  # Ярко-желтый цвет
        (source['x'], source['y']),     # Позиция
        current_radius                  # Текущий радиус с учетом пульсации
    )
    
    # Создаем эффект свечения с прозрачностью
    glow = Surface((current_radius*4, current_radius*4), SRCALPHA)
    draw.circle(
        glow,
        (255, 200, 0, 50),             # Желтый с прозрачностью
        (current_radius*2, current_radius*2),  # Центр поверхности
        current_radius*2               # Радиус свечения
    )
    screen.blit(glow, (source['x'] - current_radius*2, source['y'] - current_radius*2))

def main():
    # Основной игровой цикл
    game_running = True
    while game_running:
        
        # Обработка системных событий
        for e in event.get():
            if e.type == QUIT:
                game_running = False
        
        # Обработка пользовательского ввода
        keys = key.get_pressed()
        
        # Флаг активности персонажа
        is_moving = False
        
        # Определение режима движения
        is_running = keys[K_LSHIFT] or keys[K_RSHIFT]
        
        # Обработка горизонтального движения
        if keys[K_a] and hero.x >= 0:
            hero.facing_right = False
            speed = RUN_SPEED if is_running else WALK_SPEED
            hero.x -= speed
            hero.change_animation("run" if is_running else "walk")
            is_moving = True
        
        if keys[K_d] and hero.x <= SCREEN_WIDTH - 32:
            hero.facing_right = True
            speed = RUN_SPEED if is_running else WALK_SPEED
            hero.x += speed
            hero.change_animation("run" if is_running else "walk")
            is_moving = True
        
        # Обработка прыжка
        if keys[K_w] and hero.speed_y == 0:
            hero.speed_y = JUMP_POWER
            hero.change_animation("jump")
        
    
        # Возврат к базовой анимации при бездействии
        if not is_moving and hero.speed_y == 0:
            hero.change_animation("punch")
        
        # Обновление состояния персонажа
        hero.update()
        
        # Обновление состояния игры
        source['timer'] += 0.1             # Увеличиваем таймер анимации
        create_particles()                 # Создаем новые частицы
        update_particles()                 # Обновляем существующие частицы

        screen.fill((86, 193, 168))

        draw_particles()                   # Рисуем все частицы
        draw_source()                      # Рисуем источник
        # Отрисовка сцены

        
        hero.draw(screen)
        
        
        # Обновление дисплея
        display.flip()
        
        # Контроль частоты кадров
        clock.tick(FPS)
    
    # Завершение работы
    quit()


# Точка входа в программу
if __name__ == "__main__":
    main() 