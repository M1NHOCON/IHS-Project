#!/usr/bin/env python3
"""
Smoke test de I/O na placa (rodar NA DE2i-150, sem pygame).

Objetivos:
  1. Validar /dev/de2i150_dev (open/read/write de 32 bits).
  2. Espelhar o teste do Verilog: SW -> LEDR (mexa nas chaves, veja os LEDs).
  3. Descobrir/confirmar os offsets, varrendo HWTEST_SWEEP e imprimindo os
     valores lidos (mexa em UMA chave/botao e veja qual offset muda).
  4. Escrever um numero nos displays de 7 segmentos.

Uso (provavelmente precisa de sudo):
    sudo python3 hwtest.py           # modo interativo (menu)
    sudo python3 hwtest.py mirror    # so SW->LEDR
    sudo python3 hwtest.py sweep     # so a varredura de leitura
    sudo python3 hwtest.py hex 1234  # escreve 1234 nos displays
"""

import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import settings
from hardware.base import pack_two_hex, pack_four_hex, number_to_digits


def open_dev():
    try:
        return os.open(settings.DEVICE_PATH, os.O_RDWR)
    except OSError as e:
        print("ERRO ao abrir %s: %s" % (settings.DEVICE_PATH, e))
        print("O driver foi carregado (insmod)? Tem permissao (sudo)?")
        sys.exit(1)


def r32(fd, off):
    return struct.unpack("<I", os.pread(fd, 4, off))[0]


def w32(fd, off, val):
    os.pwrite(fd, struct.pack("<I", val & 0xFFFFFFFF), off)


def cmd_mirror(fd):
    print("SW -> LEDR. Mexa nas chaves. Ctrl+C para sair.")
    try:
        while True:
            sw = r32(fd, settings.OFF_SWITCHES) & 0x3FFFF
            w32(fd, settings.OFF_RED_LEDS, sw)
            print("\rSW=0x%05X" % sw, end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nfim.")


def cmd_sweep(fd):
    print("Lendo os offsets de HWTEST_SWEEP. Mexa em UMA chave/botao por vez")
    print("e observe qual endereco muda. Ctrl+C para sair.\n")
    try:
        while True:
            parts = []
            for off in settings.HWTEST_SWEEP:
                parts.append("%04X=%08X" % (off, r32(fd, off)))
            print("\r" + "  ".join(parts), end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nfim.")


def cmd_hex(fd, value):
    digits = number_to_digits(value, 8)
    w32(fd, settings.OFF_HEX_0_3, pack_four_hex(digits[0], digits[1],
                                                digits[2], digits[3]))
    w32(fd, settings.OFF_HEX_4_5, pack_two_hex(digits[4], digits[5]))
    w32(fd, settings.OFF_HEX_6_7, pack_two_hex(digits[6], digits[7]))
    print("Escrito %d nos displays de 7 segmentos." % value)


def cmd_keys(fd):
    print("Leitura dos botoes (KEY). Pressione-os. Ctrl+C para sair.")
    try:
        while True:
            k = r32(fd, settings.OFF_BUTTONS) & 0xF
            print("\rKEY=%s (0x%X)" % (format(k, "04b"), k), end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nfim.")


def menu(fd):
    print("=== hwtest DE2i-150 ===")
    print("1) SW -> LEDR (mirror)")
    print("2) varredura de leitura (sweep)")
    print("3) ler botoes (keys)")
    print("4) escrever numero no 7-seg")
    print("0) sair")
    ch = input("> ").strip()
    if ch == "1":
        cmd_mirror(fd)
    elif ch == "2":
        cmd_sweep(fd)
    elif ch == "3":
        cmd_keys(fd)
    elif ch == "4":
        cmd_hex(fd, int(input("numero: ").strip() or "0"))


def main():
    fd = open_dev()
    print("Dispositivo aberto: %s" % settings.DEVICE_PATH)
    try:
        if len(sys.argv) >= 2:
            cmd = sys.argv[1]
            if cmd == "mirror":
                cmd_mirror(fd)
            elif cmd == "sweep":
                cmd_sweep(fd)
            elif cmd == "keys":
                cmd_keys(fd)
            elif cmd == "hex":
                cmd_hex(fd, int(sys.argv[2]) if len(sys.argv) > 2 else 0)
            else:
                print("comando desconhecido: %s" % cmd)
        else:
            menu(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
