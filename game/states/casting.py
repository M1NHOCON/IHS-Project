"""CASTING: anima a isca saindo da vara ate o alvo escolhido na mira."""

import math

import pygame

import audio
import settings
from states.base import State
from ui import hud, leds, scene, sprites


class CastingState(State):
    DURATION = 0.7   # segundos de voo

    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.fisher = sprites.fisher_anim("hook", fps=9, loop=False)
        self.start = game.rod_origin
        # alvo definido na mira; fallback seguro caso falte
        self.target = game.land_target or (scene.BOAT_X + 320, scene.WATER_Y + 8)
        # arco mais alto quando a forca foi maior
        self.arc = 60 + game.power * 70

    def enter(self):
        audio.play("splash")

    def update(self, dt, inp):
        self.t += dt
        if self.fisher:
            self.fisher.update(dt)
        if self.t >= self.DURATION:
            self.game.land_point = self.target
            from states.waiting import WaitingState
            return WaitingState(self.game)
        return self

    def _bait_pos(self):
        k = self.t / self.DURATION
        x = self.start[0] + (self.target[0] - self.start[0]) * k
        y = self.start[1] + (self.target[1] - self.start[1]) * k
        y -= math.sin(k * math.pi) * self.arc
        return x, y

    def draw(self, screen):
        g = self.game
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)
        hud.draw_scoreboard(screen, g)
        bx, by = self._bait_pos()
        scene.draw_line(screen, g.rod_origin, (bx, by))
        pygame.draw.circle(screen, settings.C_RED, (int(bx), int(by)), 5)
        hud.draw_text_center(screen, "Lancando...", 120, size=28)

    def output(self):
        return leds.make_output(red_value=self.game.power,
                                green_bits=0b0011,
                                score=self.game.score)
