"""
Singleton com todos os sprites do jogo (frames + imagens estaticas).

Chame sprites.init() UMA vez, depois que o display do pygame existir
(em main.py, apos set_mode). Se algo falhar ao carregar, 'available' fica
False e a cena cai para o desenho primitivo (formas geometricas).
"""

import os

import pygame

import assets
from anim import Animation

# chaves das iscas/peixes da pasta Catch
CATCH_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "Box", "Barrel", "Chest"]

SCALE = 3          # personagens / barco

_S = None


class GameSprites:
    def __init__(self):
        F = assets.FISHERMAN_DIR
        O = assets.OBJECTS_DIR

        # Pescador: pose -> lista de frames
        self.fisher = {
            "idle": assets.load_frames(os.path.join(F, "Fisherman_idle.png"), scale=SCALE),
            "fish": assets.load_frames(os.path.join(F, "Fisherman_fish.png"), scale=SCALE),
            "hook": assets.load_frames(os.path.join(F, "Fisherman_hook.png"), scale=SCALE),
            "row":  assets.load_frames(os.path.join(F, "Fisherman_row.png"), scale=SCALE),
        }

        # Objetos estaticos
        self.boat = assets.load_scaled(os.path.join(O, "Boat.png"), SCALE)
        self.hut = assets.load_scaled(os.path.join(O, "Fishing_hut.png"), 1)
        self.water = assets.load_image(os.path.join(O, "Water.png"))
        self.grass = assets.load_scaled(os.path.join(O, "Grass2.png"), 2)

        # Peixes/iscas da pasta Catch. Os peixes 1-8 sao tiras com 2 frames
        # (mesmo peixe virado p/ direita e p/ esquerda); usamos so o frame 0.
        # Box/Barrel/Chest sao imagens unicas.
        self.catch = {}
        for k in CATCH_KEYS:
            nf = 1 if k in ("Box", "Barrel", "Chest") else 2
            self.catch[k] = assets.load_strip(
                os.path.join(assets.CATCH_DIR, k + ".png"), nf)
        self._catch_scaled = {}

        # Icones 32x32 (Icons_01 .. Icons_20).
        self.icons_raw = {n: assets.load_image(
            os.path.join(assets.ICONS_DIR, "Icons_%02d.png" % n)) for n in range(1, 21)}
        self._icon_scaled = {}

    def catch_image(self, key, target_h):
        """Sprite de peixe escalado para uma altura alvo (cacheado)."""
        ck = (key, target_h)
        img = self._catch_scaled.get(ck)
        if img is None:
            raw = self.catch[key][0]      # frame 0 (peixe virado p/ direita)
            s = target_h / raw.get_height()
            img = pygame.transform.scale(
                raw, (max(1, int(raw.get_width() * s)), target_h))
            self._catch_scaled[ck] = img
        return img

    def icon(self, n, size=32):
        ik = (n, size)
        img = self._icon_scaled.get(ik)
        if img is None:
            img = pygame.transform.scale(self.icons_raw[n], (size, size))
            self._icon_scaled[ik] = img
        return img


def init():
    """Carrega tudo. Retorna True se OK."""
    global _S
    try:
        _S = GameSprites()
        return True
    except (OSError, ValueError) as e:
        print("[sprites] falha ao carregar assets (%s). Usando visual simples." % e)
        _S = None
        return False


def available():
    return _S is not None


def get():
    return _S


# --- fabricas de animacao (retornam None se os assets nao carregaram) ---
def fisher_anim(pose, fps=6, loop=True):
    if _S is None:
        return None
    return Animation(_S.fisher[pose], fps=fps, loop=loop)
