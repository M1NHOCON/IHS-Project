"""
Contrato comum dos backends de hardware + utilitarios de 7 segmentos.

A ideia: o jogo nunca fala diretamente com /dev. Ele fala com um
HardwareBackend, que pode ser o FPGA real (de2i150.py) ou o teclado/tela
para desenvolvimento (keyboard.py).
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class OutputState:
    """Estado dos saidas que o jogo quer mostrar nos perifericos.

    red:        mascara de 18 bits para LEDR[17:0]
    green:      mascara de 4 bits para LEDG[3:0]
    hex_digits: 8 posicoes (HEX0..HEX7). Cada item e 0-15 (digito hex) ou
                None para apagado.
    """
    red: int = 0
    green: int = 0
    hex_digits: List = field(default_factory=lambda: [None] * 8)


# ----------------------------------------------------------------------------
# Tabela de 7 segmentos.
#
# Bits do padrao "aceso" (bit0=a ... bit6=g, 1 = segmento ligado).
# Os HEX da DE2i-150 sao ATIVO-BAIXO: no barramento, 0 acende o segmento.
# Por isso a saida final e (~padrao) & 0x7F.
# ----------------------------------------------------------------------------
_SEG_ON = {
    0x0: 0x3F, 0x1: 0x06, 0x2: 0x5B, 0x3: 0x4F,
    0x4: 0x66, 0x5: 0x6D, 0x6: 0x7D, 0x7: 0x07,
    0x8: 0x7F, 0x9: 0x6F, 0xA: 0x77, 0xB: 0x7C,
    0xC: 0x39, 0xD: 0x5E, 0xE: 0x79, 0xF: 0x71,
}
SEG_BLANK_ACTIVE_LOW = 0x7F   # todos apagados (ativo-baixo)


def digit_to_active_low(d) -> int:
    """Converte um digito (0-15) ou None no valor de 7 bits ativo-baixo."""
    if d is None:
        return SEG_BLANK_ACTIVE_LOW
    return (~_SEG_ON[d & 0xF]) & 0x7F


def digit_to_segments_on(d) -> int:
    """Padrao 'aceso' (1 = ligado), util para desenhar o display na tela."""
    if d is None:
        return 0
    return _SEG_ON[d & 0xF]


def pack_two_hex(low, high) -> int:
    """Empacota dois digitos em um barramento (HEXa em [6:0], HEXb em [14:8])."""
    return digit_to_active_low(low) | (digit_to_active_low(high) << 8)


def pack_four_hex(d0, d1, d2, d3) -> int:
    """Empacota quatro digitos (HEX0..3) em [6:0],[14:8],[22:16],[30:24]."""
    return (digit_to_active_low(d0)
            | (digit_to_active_low(d1) << 8)
            | (digit_to_active_low(d2) << 16)
            | (digit_to_active_low(d3) << 24))


def number_to_digits(value: int, width: int = 8):
    """Quebra um inteiro nao-negativo em lista de digitos (HEX0..),
    preenchendo com None as casas a esquerda. HEX0 = menos significativo."""
    value = max(0, int(value))
    digits = [None] * width
    i = 0
    if value == 0:
        digits[0] = 0
        return digits
    while value > 0 and i < width:
        digits[i] = value % 10
        value //= 10
        i += 1
    return digits


class HardwareBackend:
    """Interface que todo backend implementa."""

    def read_inputs(self) -> Tuple[int, int]:
        """Retorna (switches_mask_18b, keys_mask_4b)."""
        raise NotImplementedError

    def write_outputs(self, out: OutputState) -> None:
        """Aplica LEDs/7-seg nos perifericos (ou na tela, no sim)."""
        raise NotImplementedError

    def draw_overlay(self, screen) -> None:
        """Opcional: backend de sim desenha o painel virtual da placa."""
        pass

    def close(self) -> None:
        pass
