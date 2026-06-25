"""
Desenho do "mundo": ceu, cabana, agua animada, barco, pescador, criaturas e
a linha de pesca. Usa os sprites de ui/sprites; se indisponiveis, cai para
formas geometricas simples.
"""

import math

import pygame

import settings
from ui import sprites

# --- geometria do cenario ---
WATER_Y = 340
BOAT_X = 215

_bg = None              # surface de fundo pre-renderizada (ceu + cabana)
_water_tile = None      # faixa de agua para tiling


def rod_origin(game):
    """Ponta da vara (de onde sai a linha). Aproximada pela geometria."""
    return (BOAT_X + 93, WATER_Y - 40)


# ---------------------------------------------------------------------------
# Fundo (pre-renderizado uma vez)
# ---------------------------------------------------------------------------
def _build_bg():
    global _bg
    surf = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H))
    # gradiente de ceu
    top = (120, 196, 230)
    bot = (205, 232, 245)
    for y in range(WATER_Y):
        k = y / WATER_Y
        c = (int(top[0] + (bot[0] - top[0]) * k),
             int(top[1] + (bot[1] - top[1]) * k),
             int(top[2] + (bot[2] - top[2]) * k))
        pygame.draw.line(surf, c, (0, y), (settings.SCREEN_W, y))
    # agua base (cor solida) abaixo da linha d'agua
    surf.fill(settings.C_WATER, (0, WATER_Y, settings.SCREEN_W,
                                 settings.SCREEN_H - WATER_Y))
    # cabana de pesca ao fundo, a direita
    if sprites.available():
        hut = sprites.get().hut
        surf.blit(hut, (settings.SCREEN_W - hut.get_width() - 20,
                        WATER_Y - hut.get_height() + 8))
    _bg = surf


def _get_water_tile():
    global _water_tile
    if _water_tile is None and sprites.available():
        w = sprites.get().water
        band = w.subsurface((0, 0, w.get_width(), 28)).copy()
        _water_tile = pygame.transform.scale(band, (band.get_width() * 2, 28 * 2))
    return _water_tile


# ---------------------------------------------------------------------------
# Mundo
# ---------------------------------------------------------------------------
def draw_world(screen):
    if _bg is None:
        _build_bg()
    screen.blit(_bg, (0, 0))
    _draw_water(screen)


def _draw_water(screen):
    tile = _get_water_tile()
    t = pygame.time.get_ticks() / 1000.0
    if tile:
        tw, th = tile.get_width(), tile.get_height()
        offset = int((t * 18) % tw)
        y = WATER_Y
        row = 0
        while y < settings.SCREEN_H:
            x = -offset if row % 2 == 0 else -tw + offset
            while x < settings.SCREEN_W:
                screen.blit(tile, (x, y))
                x += tw
            # escurece com a profundidade
            shade = min(150, row * 22)
            if shade:
                dark = pygame.Surface((settings.SCREEN_W, th), pygame.SRCALPHA)
                dark.fill((0, 20, 50, shade))
                screen.blit(dark, (0, y))
            y += th
            row += 1
    # linha de espuma na superficie
    pts = [(x, WATER_Y + int(math.sin(x * 0.05 + t * 3) * 2))
           for x in range(0, settings.SCREEN_W + 1, 16)]
    pygame.draw.lines(screen, settings.C_WHITE, False, pts, 2)


def draw_boat(screen):
    t = pygame.time.get_ticks() / 1000.0
    bob = int(math.sin(t * 1.5) * 3)
    if sprites.available():
        boat = sprites.get().boat
        rect = boat.get_rect(center=(BOAT_X, WATER_Y + 10 + bob))
        screen.blit(boat, rect)
    else:
        y = WATER_Y + bob
        pygame.draw.polygon(screen, (110, 70, 40),
                            [(BOAT_X - 60, y), (BOAT_X + 60, y),
                             (BOAT_X + 40, y + 26), (BOAT_X - 40, y + 26)])


def draw_fisherman(screen, anim):
    """Desenha o pescador (frame atual de 'anim') sentado no barco."""
    t = pygame.time.get_ticks() / 1000.0
    bob = int(math.sin(t * 1.5) * 3)
    if sprites.available() and anim is not None and anim.image():
        img = anim.image()
        rect = img.get_rect()
        rect.midbottom = (BOAT_X - 6, WATER_Y + 24 + bob)
        screen.blit(img, rect)
    else:
        x, y = BOAT_X - 6, WATER_Y - 30 + bob
        pygame.draw.circle(screen, (40, 40, 60), (x, y - 10), 9)
        pygame.draw.rect(screen, (40, 40, 60), (x - 6, y, 12, 22))


def draw_line(screen, p1, p2):
    """Linha de pesca com uma leve catenaria."""
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2 + 14
    steps = 14
    pts = []
    for i in range(steps + 1):
        u = i / steps
        x = (1 - u) ** 2 * p1[0] + 2 * (1 - u) * u * mx + u * u * p2[0]
        y = (1 - u) ** 2 * p1[1] + 2 * (1 - u) * u * my + u * u * p2[1]
        pts.append((x, y))
    pygame.draw.lines(screen, settings.C_WHITE, False, pts, 1)


def draw_bobber(screen, pos):
    t = pygame.time.get_ticks() / 1000.0
    y = pos[1] + math.sin(t * 4) * 3
    pygame.draw.circle(screen, settings.C_RED, (int(pos[0]), int(y)), 6)
    pygame.draw.circle(screen, settings.C_WHITE, (int(pos[0]), int(y)), 6, 1)


def catch_height(size):
    """Altura na tela (px) da isca, conforme o 'tamanho' do peixe."""
    return 18 + int(size) * 4


def draw_catch(screen, fish, center, flip=True, wiggle=True):
    """Desenha a isca/peixe (sprite estatico) com um balanco de 'natacao'."""
    if not sprites.available() or fish is None:
        pygame.draw.circle(screen, (90, 170, 90),
                           (int(center[0]), int(center[1])), 16)
        return
    img = sprites.get().catch_image(fish.sprite, catch_height(fish.size))
    if flip:
        img = pygame.transform.flip(img, True, False)
    if wiggle:
        t = pygame.time.get_ticks() / 1000.0
        img = pygame.transform.rotate(img, math.sin(t * 6) * 8)
    screen.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))
