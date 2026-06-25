"""
Backend real: fala com o FPGA via /dev/de2i150_dev (driver PCIe/Character).

Mesma semantica do app/main.c, em Python: o driver le/escreve sempre 4 bytes
(uint32) no offset passado (ver de2i150_read/de2i150_write no driver).
"""

import os
import struct

import settings
from hardware.base import (
    HardwareBackend, OutputState,
    pack_two_hex, pack_four_hex,
)


class De2i150Backend(HardwareBackend):
    def __init__(self, path: str = settings.DEVICE_PATH):
        self.path = path
        # O_RDWR: precisamos ler (botoes/switches) e escrever (leds/hex).
        self.fd = os.open(path, os.O_RDWR)

    # --- acesso cru de 32 bits -------------------------------------------
    def _read32(self, off: int) -> int:
        data = os.pread(self.fd, 4, off)
        return struct.unpack("<I", data)[0]

    def _write32(self, off: int, val: int) -> None:
        os.pwrite(self.fd, struct.pack("<I", val & 0xFFFFFFFF), off)

    # --- entradas ---------------------------------------------------------
    def read_inputs(self):
        switches = self._read32(settings.OFF_SWITCHES) & 0x3FFFF   # 18 bits
        # keys_bus = ~KEY no Verilog -> bit 1 ja significa "pressionado".
        keys = self._read32(settings.OFF_BUTTONS) & 0xF            # 4 bits
        return switches, keys

    # --- saidas -----------------------------------------------------------
    def write_outputs(self, out: OutputState):
        self._write32(settings.OFF_RED_LEDS, out.red & 0x3FFFF)
        self._write32(settings.OFF_GREEN_LEDS, out.green & 0xF)

        d = out.hex_digits
        self._write32(settings.OFF_HEX_0_3, pack_four_hex(d[0], d[1], d[2], d[3]))
        self._write32(settings.OFF_HEX_4_5, pack_two_hex(d[4], d[5]))
        self._write32(settings.OFF_HEX_6_7, pack_two_hex(d[6], d[7]))

    def close(self):
        try:
            # Apaga tudo ao sair, para nao deixar LED/HEX presos.
            self.write_outputs(OutputState())
        except OSError:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass
