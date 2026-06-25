"""WAITING: espera aleatoria ate o peixe morder. Boia balanca na agua."""

import math
import random

import pygame

import settings
from states.base import State
from ui import hud, leds


class WaitingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.wait = random.uniform(settings.WAIT_MIN, settings.WAIT_MAX)

    def update(self, dt, inp):
        self.t += dt
        if self.t >= self.wait:
            from states.hooked import HookedState
            return HookedState(self.game)
        return self

    def draw(self, screen):
        g = self.game
        hud.draw_scene(screen)
        hud.draw_boat(screen, g.boat_x)
        lp = g.land_point
        if lp:
            # boia balancando
            by = lp[1] + math.sin(self.t * 4) * 4
            pygame.draw.line(screen, settings.C_WHITE, g.rod_origin,
                             (lp[0], by), 1)
            pygame.draw.circle(screen, settings.C_RED, (int(lp[0]), int(by)), 6)
            pygame.draw.circle(screen, settings.C_WHITE, (int(lp[0]), int(by)), 6, 1)
        hud.draw_text_center(screen, "Aguardando a mordida...", 250, size=26)

    def output(self):
        # pulso lento nos LEDR enquanto espera
        v = (math.sin(self.t * 3) + 1) / 2 * 0.3
        return leds.make_output(red_value=v, green_bits=0b0010,
                                score=self.game.score)
