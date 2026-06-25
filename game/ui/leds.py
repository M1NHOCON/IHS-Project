"""
Helpers para traduzir grandezas do jogo (0..1) em mascaras de LED e para
montar o OutputState (LEDR + LEDG + HEX).
"""

from hardware.base import OutputState, number_to_digits
import settings


def bar_mask(value: float, width: int = 18) -> int:
    """value 0..1 -> barra de LEDs acesa da direita para a esquerda."""
    value = max(0.0, min(1.0, value))
    n = int(round(value * width))
    if n <= 0:
        return 0
    return (1 << n) - 1


def make_output(red_value: float = 0.0,
                green_bits: int = 0,
                score: int = None,
                blink_red: bool = False) -> OutputState:
    """Monta um OutputState.

    red_value  : 0..1 vira barra nos LEDR (tensao/progresso)
    green_bits : mascara crua p/ LEDG (fase do jogo)
    score      : se dado, mostrado nos HEX
    blink_red  : se True, acende TODOS os LEDR (flash de fisgada)
    """
    out = OutputState()
    out.red = 0x3FFFF if blink_red else bar_mask(red_value, 18)
    out.green = green_bits & 0xF
    if score is not None:
        out.hex_digits = number_to_digits(score, 8)
    return out
