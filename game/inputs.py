"""
Estado de entrada com deteccao de borda em software.

Comparamos o frame atual com o anterior para gerar key_pressed (borda de
subida) e key_released (borda de descida) sem depender da config de
EDGE_CAP do PIO no FPGA.
"""


class InputState:
    def __init__(self):
        self.switches = 0
        self.keys = 0
        self._keys_prev = 0

    def update(self, switches: int, keys: int):
        self._keys_prev = self.keys
        self.switches = switches
        self.keys = keys

    # --- switches ---
    def switch_on(self, i: int) -> bool:
        return bool((self.switches >> i) & 1)

    # --- botoes (nivel) ---
    def key_down(self, i: int) -> bool:
        return bool((self.keys >> i) & 1)

    # --- botoes (bordas) ---
    def key_pressed(self, i: int) -> bool:
        return bool(((self.keys >> i) & 1) and not ((self._keys_prev >> i) & 1))

    def key_released(self, i: int) -> bool:
        return bool(not ((self.keys >> i) & 1) and ((self._keys_prev >> i) & 1))
