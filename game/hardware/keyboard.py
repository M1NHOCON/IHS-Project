"""
Backend de simulacao: usa o teclado como entradas e desenha um "painel
virtual" da placa (LEDR / LEDG / HEX) na propria tela.

Permite desenvolver toda a logica do jogo no laptop, sem a placa.

Mapeamento de teclas:
  KEY[3] (acao: lancar/fisgar) ...... ESPACO
  KEY[0] (esquerda / manivela A) .... SETA ESQUERDA  ou  A
  KEY[1] (direita  / manivela B) .... SETA DIREITA   ou  D
  KEY[2] (extra) .................... SETA CIMA       ou  W
  SW[0]  (dar linha) ................ SHIFT ESQUERDO (segurar)
  SW[1..3] ............................ teclas 2,3,4 (segurar) - debug
"""

import pygame

import settings
from hardware.base import (
    HardwareBackend, OutputState,
    digit_to_segments_on,
)

# tecla pygame -> indice de KEY
_KEY_MAP = {
    pygame.K_SPACE: settings.KEY_ACTION,
    pygame.K_LEFT:  settings.KEY_LEFT,
    pygame.K_a:     settings.KEY_LEFT,
    pygame.K_RIGHT: settings.KEY_RIGHT,
    pygame.K_d:     settings.KEY_RIGHT,
    pygame.K_UP:    settings.KEY_EXTRA,
    pygame.K_w:     settings.KEY_EXTRA,
}

# tecla pygame -> indice de SW (segurar = ligado)
_SW_MAP = {
    pygame.K_LSHIFT: settings.SW_GIVE_LINE,
    pygame.K_2: 1,
    pygame.K_3: 2,
    pygame.K_4: 3,
}


class KeyboardBackend(HardwareBackend):
    def __init__(self):
        self._last_out = OutputState()

    def read_inputs(self):
        pressed = pygame.key.get_pressed()

        keys = 0
        for pgk, idx in _KEY_MAP.items():
            if pressed[pgk]:
                keys |= (1 << idx)

        switches = 0
        for pgk, idx in _SW_MAP.items():
            if pressed[pgk]:
                switches |= (1 << idx)

        return switches, keys

    def write_outputs(self, out: OutputState):
        # No sim nao ha placa: so guardamos para desenhar no overlay.
        self._last_out = out

    # ------------------------------------------------------------------
    # Painel virtual da placa, desenhado no rodape da tela.
    # ------------------------------------------------------------------
    def draw_overlay(self, screen):
        out = self._last_out
        w = screen.get_width()
        panel_h = 96
        y0 = screen.get_height() - panel_h

        pygame.draw.rect(screen, settings.C_PANEL, (0, y0, w, panel_h))
        pygame.draw.line(screen, settings.C_BLACK, (0, y0), (w, y0), 2)

        # --- LEDR (18) ---
        self._draw_led_row(screen, "LEDR", out.red, 18, settings.C_RED,
                           x=12, y=y0 + 10, size=14)
        # --- LEDG (4) ---
        self._draw_led_row(screen, "LEDG", out.green, 4, settings.C_GREEN,
                           x=12, y=y0 + 40, size=14)
        # --- HEX0..7 ---
        self._draw_hex(screen, out.hex_digits, x=w - 8, y=y0 + 12)

    def _draw_led_row(self, screen, label, mask, count, color, x, y, size):
        font = pygame.font.SysFont("monospace", 13)
        screen.blit(font.render(label, True, settings.C_WHITE), (x, y))
        bx = x + 48
        # bit mais significativo a esquerda (como na placa).
        for i in range(count - 1, -1, -1):
            on = (mask >> i) & 1
            c = color if on else settings.C_LED_OFF
            pygame.draw.rect(screen, c, (bx, y, size - 3, size - 3))
            bx += size

    def _draw_hex(self, screen, digits, x, y):
        # desenha HEX7..HEX0 da direita para a esquerda.
        dw, dh, pad = 26, 46, 6
        bx = x - dw
        for i in range(8):                     # i = 0 (HEX0) ... 7 (HEX7)
            seg = digit_to_segments_on(digits[i])
            self._draw_7seg(screen, seg, bx - i * (dw + pad), y, dw, dh)

    def _draw_7seg(self, screen, seg_on, x, y, w, h):
        on = settings.C_RED
        off = (45, 20, 20)
        t = 4                                   # espessura do segmento
        mid = y + h // 2
        # a,b,c,d,e,f,g
        segs = {
            0: (x + t, y, w - 2 * t, t),                 # a (topo)
            1: (x + w - t, y + t, t, h // 2 - t),        # b (sup dir)
            2: (x + w - t, mid + 1, t, h // 2 - t),      # c (inf dir)
            3: (x + t, y + h - t, w - 2 * t, t),         # d (base)
            4: (x, mid + 1, t, h // 2 - t),              # e (inf esq)
            5: (x, y + t, t, h // 2 - t),                # f (sup esq)
            6: (x + t, mid - t // 2, w - 2 * t, t),      # g (meio)
        }
        for bit, rect in segs.items():
            c = on if (seg_on >> bit) & 1 else off
            pygame.draw.rect(screen, c, rect)
