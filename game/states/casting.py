"""CASTING: anima a isca saindo da vara ate cair na agua (angulo + forca)."""

import math

import pygame

import audio
import settings
from states.base import State
from ui import hud, leds


class CastingState(State):
    DURATION = 0.7   # segundos de voo

    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        g = game
        ox, oy = g.rod_origin
        rad = math.radians(g.aim_angle)
        # alcance proporcional a forca
        reach = 120 + g.power * 360
        self.start = (ox, oy)
        self.target = (ox + reach * math.cos(rad), hud.WATER_Y + 8)

    def enter(self):
        audio.play("splash")

    def update(self, dt, inp):
        self.t += dt
        if self.t >= self.DURATION:
            # fixa onde caiu e vai esperar
            self.game.land_point = self.target
            from states.waiting import WaitingState
            return WaitingState(self.game)
        return self

    def _bait_pos(self):
        # interpolacao com um arco (parabola simples)
        k = self.t / self.DURATION
        x = self.start[0] + (self.target[0] - self.start[0]) * k
        y = self.start[1] + (self.target[1] - self.start[1]) * k
        y -= math.sin(k * math.pi) * 80   # altura do arco
        return x, y

    def draw(self, screen):
        g = self.game
        hud.draw_scene(screen)
        hud.draw_boat(screen, g.boat_x)
        bx, by = self._bait_pos()
        # linha da vara ate a isca
        pygame.draw.line(screen, settings.C_WHITE, g.rod_origin, (bx, by), 1)
        pygame.draw.circle(screen, settings.C_RED, (int(bx), int(by)), 5)
        hud.draw_text_center(screen, "Lancando...", 250, size=26)

    def output(self):
        return leds.make_output(red_value=self.game.power,
                                green_bits=0b0011,
                                score=self.game.score)
