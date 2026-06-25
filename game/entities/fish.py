"""
Peixe (captura): usa os sprites estaticos da pasta Catch.

  sprite = chave em ui/sprites.CATCH_KEYS ("1".."8", "Box", "Barrel", "Chest")
  kind   = "fish" (peixe), "junk" (lixo) ou "treasure" (tesouro)

Peixe grande da mais pontos, mas corre mais (sobe a tensao) e e mais facil
de arrebentar a linha -> exige controle fino. Lixo quase nao luta e vale
pouco; o bau e raro e vale muito.
"""

import random
from dataclasses import dataclass


@dataclass
class Fish:
    name: str
    size: int           # tambem vira pontos
    sprite: str         # chave da imagem na pasta Catch
    run_chance: float
    run_power: float
    reel_factor: float
    kind: str = "fish"

    @property
    def points(self) -> int:
        return self.size


# name,            size, sprite,  run_chance, run_power, reel_factor, kind,       peso
_CATALOG = [
    ("Lambari",       1, "1",  0.15, 0.18, 1.50, "fish",     26),
    ("Sardinha",      2, "2",  0.22, 0.25, 1.30, "fish",     22),
    ("Piaba",         2, "8",  0.25, 0.28, 1.30, "fish",     18),
    ("Tilapia",       3, "3",  0.35, 0.40, 1.10, "fish",     16),
    ("Tucunare",      4, "4",  0.50, 0.55, 0.95, "fish",     12),
    ("Traira",        5, "7",  0.60, 0.62, 0.85, "fish",      9),
    ("Dourado",       7, "5",  0.75, 0.80, 0.70, "fish",      5),
    ("Pirarucu",      9, "6",  0.88, 0.95, 0.60, "fish",      3),
    ("Caixa velha",   0, "Box",    0.10, 0.15, 1.70, "junk",     5),
    ("Barril",        1, "Barrel", 0.12, 0.18, 1.60, "junk",     4),
    ("Bau do tesouro", 15, "Chest", 0.70, 0.70, 0.70, "treasure", 2),
]


def random_fish() -> Fish:
    weights = [c[7] for c in _CATALOG]
    name, size, sprite, rc, rp, rf, kind, _ = random.choices(
        _CATALOG, weights=weights, k=1)[0]
    return Fish(name=name, size=size, sprite=sprite,
                run_chance=rc, run_power=rp, reel_factor=rf, kind=kind)
