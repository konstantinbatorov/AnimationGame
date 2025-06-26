"""
Демонстрация системы частиц с центральным источником
Желтый пульсирующий круг испускает частицы-искры
"""

import pygame
import random
import math

# Инициализация Pygame и создание окна
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Система частиц - Центральный источник")
clock = pygame.time.Clock()

# Глобальные переменные
particles = []  # Список для хранения всех активных частиц

# Параметры источника частиц (желтого круга)
source = {
    'x': 400,      # X-координата центра
    'y': 300,      # Y-координата центра
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
        pygame.draw.circle(
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
    pygame.draw.circle(
        screen,
        (255, 255, 0),                  # Ярко-желтый цвет
        (source['x'], source['y']),     # Позиция
        current_radius                  # Текущий радиус с учетом пульсации
    )
    
    # Создаем эффект свечения с прозрачностью
    glow = pygame.Surface((current_radius*4, current_radius*4), pygame.SRCALPHA)
    pygame.draw.circle(
        glow,
        (255, 200, 0, 50),             # Желтый с прозрачностью
        (current_radius*2, current_radius*2),  # Центр поверхности
        current_radius*2               # Радиус свечения
    )
    screen.blit(glow, (source['x'] - current_radius*2, source['y'] - current_radius*2))

# Основной игровой цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Обновление состояния игры
    source['timer'] += 0.1             # Увеличиваем таймер анимации
    create_particles()                 # Создаем новые частицы
    update_particles()                 # Обновляем существующие частицы
    
    # Отрисовка
    screen.fill((10, 10, 30))         # Очистка экрана (темно-синий фон)
    
    draw_particles()                   # Рисуем все частицы
    draw_source()                      # Рисуем источник
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)  # Ограничение до 60 кадров в секунду

# Завершение работы
pygame.quit()