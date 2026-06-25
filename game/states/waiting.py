"""WAITING: espera aleatoria ate o peixe morder. Boia balanca na agua."""

import random

import settings
from states.base import State
from ui import hud, leds, scene, sprites


class WaitingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.wait = random.uniform(settings.WAIT_MIN, settings.WAIT_MAX)
        self.fisher = sprites.fisher_anim("fish", fps=4)

    def update(self, dt, inp):
        self.t += dt
        if self.fisher:
            self.fisher.update(dt)
        if self.t >= self.wait:
            from states.hooked import HookedState
            return HookedState(self.game)
        return self

    def draw(self, screen):
        g = self.game
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)
        hud.draw_scoreboard(screen, g)
        if g.land_point:
            scene.draw_line(screen, g.rod_origin, g.land_point)
            scene.draw_bobber(screen, g.land_point)
        hud.draw_text_center(screen, "Aguardando a mordida...", 130, size=26)

    def output(self):
        import math
        v = (math.sin(self.t * 3) + 1) / 2 * 0.3
        return leds.make_output(red_value=v, green_bits=0b0010,
                                score=self.game.score)
