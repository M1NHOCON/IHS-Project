"""
Widgets de interface desenhados POR CIMA do mundo: barras, textos e paineis.
(O cenario/personagens ficam em ui/scene.py.)
"""

import math

import pygame

import settings
from ui import sprites

# indices dos icones usados na interface (pasta 4 Icons)
ICON_HOOK = 1
ICON_FISHERMAN = 2
ICON_ROD = 3
ICON_FISH = 4
ICON_BUCKET = 16     # balde cheio de peixes
ICON_TROPHY = 14     # peixe dourado (troféu)

_font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    f = _font_cache.get(key)
    if f is None:
        f = pygame.font.SysFont("arial", size, bold=bold)
        _font_cache[key] = f
    return f


def draw_icon(screen, n, x, y, size=32):
    """Desenha um icone (canto sup-esq em x,y). No-op se nao houver sprites."""
    if sprites.available():
        screen.blit(sprites.get().icon(n, size), (x, y))


def draw_scoreboard(screen, game):
    """Placar fixo (canto sup-esq) com icones: pontos e peixes capturados."""
    draw_panel(screen, 10, 10, 196, 84)
    draw_icon(screen, ICON_BUCKET, 20, 20, 36)
    screen.blit(font(26, True).render("%d pts" % game.score, True,
                settings.C_YELLOW), (64, 24))
    draw_icon(screen, ICON_FISH, 20, 56, 28)
    screen.blit(font(20, True).render("%d peixes" % game.fish_caught, True,
                settings.C_WHITE), (60, 58))


def draw_panel(screen, x, y, w, h, alpha=150):
    """Painel translucido escuro para dar contraste ao texto."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((10, 16, 24, alpha))
    screen.blit(s, (x, y))
    pygame.draw.rect(screen, (230, 220, 180), (x, y, w, h), 2)


def draw_bar(screen, x, y, w, h, value, color, label=None, danger=False):
    """Barra horizontal 0..1, com moldura e brilho."""
    value = max(0.0, min(1.0, value))
    pygame.draw.rect(screen, (12, 16, 22), (x - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(screen, (60, 50, 35), (x, y, w, h))
    fill = color
    if danger and value > 0.8:
        # pisca quando perto de estourar
        if int(pygame.time.get_ticks() / 120) % 2 == 0:
            fill = settings.C_RED
    pygame.draw.rect(screen, fill, (x, y, int(w * value), h))
    pygame.draw.rect(screen, (230, 220, 180), (x, y, w, h), 2)
    if label:
        screen.blit(font(16, True).render(label, True, settings.C_WHITE),
                    (x, y - 22))


def draw_target_line(screen, origin, target):
    """Linha de mira pontilhada da ponta da vara ate um alvo (mira na agua)."""
    n = 14
    for i in range(n):
        if i % 2 == 0:
            a = i / n
            b = (i + 1) / n
            pygame.draw.line(
                screen, settings.C_YELLOW,
                (origin[0] + (target[0] - origin[0]) * a,
                 origin[1] + (target[1] - origin[1]) * a),
                (origin[0] + (target[0] - origin[0]) * b,
                 origin[1] + (target[1] - origin[1]) * b), 2)
    tx, ty = int(target[0]), int(target[1])
    pygame.draw.circle(screen, settings.C_YELLOW, (tx, ty), 10, 2)
    pygame.draw.line(screen, settings.C_YELLOW, (tx - 14, ty), (tx + 14, ty), 2)
    pygame.draw.line(screen, settings.C_YELLOW, (tx, ty - 14), (tx, ty + 14), 2)


def draw_text_center(screen, text, y, size=36, color=None, bold=True, shadow=True):
    color = color or settings.C_WHITE
    surf = font(size, bold).render(text, True, color)
    rect = surf.get_rect(center=(settings.SCREEN_W // 2, y))
    if shadow:
        sh = font(size, bold).render(text, True, settings.C_BLACK)
        screen.blit(sh, sh.get_rect(center=(settings.SCREEN_W // 2 + 2, y + 2)))
    screen.blit(surf, rect)


def draw_text(screen, text, x, y, size=22, color=None, bold=False, shadow=True):
    color = color or settings.C_WHITE
    if shadow:
        screen.blit(font(size, bold).render(text, True, settings.C_BLACK),
                    (x + 2, y + 2))
    screen.blit(font(size, bold).render(text, True, color), (x, y))
