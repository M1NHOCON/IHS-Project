#!/usr/bin/env python3
"""
Jogo de Pesca - Projeto IHS (DE2i-150).

Uso:
    python main.py            # auto: usa a placa se /dev existir, senao --sim
    python main.py --sim      # forca simulacao por teclado (laptop)
    python main.py --hw       # forca a placa real (/dev/de2i150_dev)

Controles (placa / teclado):
    KEY[3] / ESPACO ........ lancar e fisgar
    KEY[0] / KEY[1] (A/D) .. mirar e girar o molinete (alternar)
    SW[0]  / SHIFT ......... dar linha (aliviar tensao)
"""

import argparse
import os
import sys

# garante que os modulos de game/ sejam importaveis ao rodar de qualquer lugar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

import audio
import settings
from game import Game
from hardware.factory import make_backend
from inputs import InputState
from states.menu import MenuState


def parse_args():
    p = argparse.ArgumentParser(description="Jogo de Pesca IHS - DE2i-150")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--sim", action="store_true", help="simulacao por teclado")
    g.add_argument("--hw", action="store_true", help="forca a placa real")
    return p.parse_args()


def main():
    args = parse_args()
    mode = "sim" if args.sim else "hw" if args.hw else "auto"

    pygame.init()
    audio.init()
    screen = pygame.display.set_mode((settings.SCREEN_W, settings.SCREEN_H))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    hw, using_real = make_backend(mode)
    print("[hardware] backend: %s" % ("FPGA real" if using_real else "teclado (sim)"))

    inp = InputState()
    game = Game()
    state = MenuState(game)

    running = True
    try:
        while running:
            dt = clock.tick(settings.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # le entradas do backend (placa ou teclado) e atualiza bordas
            switches, keys = hw.read_inputs()
            inp.update(switches, keys)

            # FSM
            nxt = state.update(dt, inp)
            if nxt is not state:
                nxt.enter()
                state = nxt

            # desenho
            state.draw(screen)

            # saidas para os perifericos (LEDR/LEDG/HEX)
            out = state.output()
            hw.write_outputs(out)

            # painel virtual no modo sim
            hw.draw_overlay(screen)

            pygame.display.flip()
    finally:
        hw.close()
        pygame.quit()


if __name__ == "__main__":
    main()
