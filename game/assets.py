"""
Carregamento e cache de imagens / sprite sheets.

Importante: nada e carregado no import. Os loaders so funcionam depois que o
display do pygame existe (convert_alpha precisa de video mode). Por isso tudo
e carregado sob demanda (lazy) e cacheado.
"""

import os

import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FISH_PACK = os.path.join(
    ASSETS_DIR, "craftpix-net-258377-free-fishing-game-assets-pixel-art-pack (1)")
SEA_PACK = os.path.join(
    ASSETS_DIR,
    "craftpix-net-800891-octopus-jellyfish-shark-and-turtle-free-sprite-pixel-art")
FISHERMAN_DIR = os.path.join(FISH_PACK, "1 Fisherman")
OBJECTS_DIR = os.path.join(FISH_PACK, "3 Objects")
CATCH_DIR = os.path.join(OBJECTS_DIR, "Catch")
ICONS_DIR = os.path.join(FISH_PACK, "4 Icons")

_cache = {}


def _scale(img, scale):
    if scale == 1:
        return img
    w, h = img.get_width(), img.get_height()
    return pygame.transform.scale(img, (int(w * scale), int(h * scale)))


def load_image(path):
    img = _cache.get(path)
    if img is None:
        img = pygame.image.load(path).convert_alpha()
        _cache[path] = img
    return img


def load_scaled(path, scale=1):
    key = (path, "scaled", scale)
    img = _cache.get(key)
    if img is None:
        img = _scale(load_image(path), scale)
        _cache[key] = img
    return img


def load_strip(path, frames=2, scale=1):
    """Fatia uma imagem em N frames de largura igual (altura cheia)."""
    key = (path, "strip", frames, scale)
    out = _cache.get(key)
    if out is None:
        sheet = load_image(path)
        fw = sheet.get_width() // frames
        fh = sheet.get_height()
        out = [_scale(sheet.subsurface((i * fw, 0, fw, fh)).copy(), scale)
               for i in range(frames)]
        _cache[key] = out
    return out


def load_frames(path, fw=48, fh=48, scale=1):
    """Fatia uma tira horizontal em frames de fw x fh (com escala opcional)."""
    key = (path, fw, fh, scale)
    frames = _cache.get(key)
    if frames is None:
        sheet = load_image(path)
        n = max(1, sheet.get_width() // fw)
        frames = []
        for i in range(n):
            fr = sheet.subsurface((i * fw, 0, fw, fh)).copy()
            frames.append(_scale(fr, scale))
        _cache[key] = frames
    return frames
