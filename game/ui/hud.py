"""
Funcoes de desenho reaproveitadas pelos estados (cenario e widgets).
"""

import math
import pygame

import settings

# linha d'agua (em pixels) - tudo abaixo disso e agua.
WATER_Y = 300


def draw_scene(screen):
    """Ceu + agua + onda simples."""
    screen.fill(settings.C_SKY)
    pygame.draw.rect(screen, settings.C_WATER,
                     (0, WATER_Y, settings.SCREEN_W, settings.SCREEN_H - WATER_Y))
    # faixa mais escura no fundo
    pygame.draw.rect(screen, settings.C_WATER_DK,
                     (0, WATER_Y + 140, settings.SCREEN_W,
                      settings.SCREEN_H - WATER_Y - 140))
    pygame.draw.line(screen, settings.C_WHITE, (0, WATER_Y),
                     (settings.SCREEN_W, WATER_Y), 2)


def draw_boat(screen, x=120):
    """Barquinho + pescador estilizado, na superficie."""
    y = WATER_Y
    pygame.draw.polygon(screen, (110, 70, 40),
                        [(x - 45, y), (x + 45, y), (x + 30, y + 22), (x - 30, y + 22)])
    # pescador
    pygame.draw.circle(screen, (40, 40, 60), (x, y - 28), 8)
    pygame.draw.rect(screen, (40, 40, 60), (x - 5, y - 22, 10, 18))


def rod_tip(boat_x=120):
    """Ponta da vara, de onde sai a linha."""
    return (boat_x + 40, WATER_Y - 40)


def draw_bar(screen, x, y, w, h, value, color, label=None, danger=False):
    """Barra horizontal generica 0..1."""
    value = max(0.0, min(1.0, value))
    pygame.draw.rect(screen, settings.C_BLACK, (x - 2, y - 2, w + 4, h + 4), 2)
    fill = color
    if danger and value > 0.8:
        fill = settings.C_RED
    pygame.draw.rect(screen, fill, (x, y, int(w * value), h))
    if label:
        font = pygame.font.SysFont("arial", 16, bold=True)
        screen.blit(font.render(label, True, settings.C_BLACK), (x, y - 22))


def draw_aim(screen, origin, angle_deg, length=140):
    """Seta de mira a partir da ponta da vara."""
    rad = math.radians(angle_deg)
    ex = origin[0] + length * math.cos(rad)
    ey = origin[1] - length * math.sin(rad)
    pygame.draw.line(screen, settings.C_YELLOW, origin, (ex, ey), 3)
    pygame.draw.circle(screen, settings.C_YELLOW, (int(ex), int(ey)), 6)
    return ex, ey


def draw_text_center(screen, text, y, size=36, color=None, bold=True):
    color = color or settings.C_BLACK
    font = pygame.font.SysFont("arial", size, bold=bold)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(settings.SCREEN_W // 2, y))
    screen.blit(surf, rect)


def draw_text(screen, text, x, y, size=22, color=None, bold=False):
    color = color or settings.C_BLACK
    font = pygame.font.SysFont("arial", size, bold=bold)
    screen.blit(font.render(text, True, color), (x, y))
