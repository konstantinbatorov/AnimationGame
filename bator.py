"""
Демонстрация системы частиц
Частицы исходят из пульсирующего желтого круга
"""

import pygame
import random
import math

# Инициализация
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Система частиц - Источник")
clock = pygame.time.Clock()

# Список частиц
particles = []

# Позиция и параметры источника
source = {
    'x': 100,
    'y': 100,
    'timer': 0,
    'radius': 30
}

def create_particles(count=5):
    """Создает частицы из центра источника"""
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
                random.randint(200, 255),  # Желто-оранжевая гамма
                random.randint(100, 200),
                random.randint(0, 50)
            ],
            'size': random.randint(3, 8)
        }
        particles.append(particle)

def update_particles():
    """Обновляет состояние всех частиц"""
    global particles
    for particle in particles[:]:
        # Движение частицы
        particle['x'] += particle['speed_x']
        particle['y'] += particle['speed_y']
        
        # Замедление
        particle['speed_x'] *= 0.98
        particle['speed_y'] *= 0.98
        
        # Гравитация
        particle['speed_y'] += 0.1
        
        # Уменьшение времени жизни
        particle['life'] -= 1
        
        # Изменение размера
        particle['size'] = max(1, particle['size'] * 0.97)
        
        # Удаление мертвых частиц
        if particle['life'] <= 0 or particle['size'] < 0.5:
            particles.remove(particle)

def draw_particles():
    """Отрисовывает все частицы"""
    for particle in particles:
        pygame.draw.circle(
            screen, 
            particle['color'], 
            (int(particle['x']), int(particle['y'])), 
            int(particle['size'])
        )

def draw_source():
    """Рисует пульсирующий источник частиц"""
    source['timer'] += 0.05
    pulse = math.sin(source['timer']) * 0.2 + 1
    current_radius = int(source['radius'] * pulse)
    
    # Ядро источника
    pygame.draw.circle(screen, (255, 255, 0), (source['x'], source['y']), current_radius)
    
    # Свечение
    glow = pygame.Surface((current_radius*4, current_radius*4), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 200, 0, 50), 
                     (current_radius*2, current_radius*2), 
                     current_radius*2)
    screen.blit(glow, (source['x'] - current_radius*2, source['y'] - current_radius*2))

# Основной цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Обновление
    source['timer'] += 0.1
    create_particles()  # Постоянное создание частиц
    update_particles()
    
    # Отрисовка
    screen.fill((10, 10, 30))  # Темный фон
    
    draw_particles()
    draw_source()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()