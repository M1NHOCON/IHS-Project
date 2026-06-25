"""
Peixe: tamanho, forca e tendencia de "correr".

Peixe grande da mais pontos, mas corre mais (sobe a tensao) e e mais facil
de arrebentar a linha -> exige controle fino.
"""

import random
from dataclasses import dataclass


@dataclass
class Fish:
    name: str
    size: int          # 1..9  (tambem vira pontos)
    color: tuple
    run_chance: float  # prob/seg de iniciar uma corrida
    run_power: float   # quanto de tensao a corrida adiciona por seg
    reel_factor: float # multiplicador de progresso por manivela (peixe pesado puxa menos)

    @property
    def points(self) -> int:
        return self.size


# Catalogo. Pesos diferentes de aparicao: peixe grande e raro.
_CATALOG = [
    # name,        size, color,            run_chance, run_power, reel_factor, peso
    ("Lambari",      1, (180, 200, 210), 0.20, 0.20, 1.40, 30),
    ("Tilapia",      3, (150, 180, 120), 0.35, 0.35, 1.10, 28),
    ("Tucunare",     5, (90, 170, 90),   0.50, 0.55, 0.90, 22),
    ("Dourado",      7, (235, 200, 70),  0.65, 0.75, 0.75, 14),
    ("Pirarucu",     9, (120, 90, 80),   0.80, 0.95, 0.60, 6),
]


def random_fish() -> Fish:
    names = [c[0] for c in _CATALOG]
    weights = [c[6] for c in _CATALOG]
    chosen = random.choices(_CATALOG, weights=weights, k=1)[0]
    name, size, color, run_chance, run_power, reel_factor, _ = chosen
    return Fish(name=name, size=size, color=color,
                run_chance=run_chance, run_power=run_power,
                reel_factor=reel_factor)
