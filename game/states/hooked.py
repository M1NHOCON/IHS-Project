"""
HOOKED: a mordida! "FISGOU!" com flash de LEDs + som.
Janela curta para KEY[3] fisgar (timing). Errar = peixe foge.
"""

import audio
import settings
from entities.fish import random_fish
from states.base import State
from ui import hud, leds, scene, sprites


class HookedState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self._blink = 0.0
        self.fisher = sprites.fisher_anim("hook", fps=12, loop=False)

    def enter(self):
        audio.play("hook")

    def update(self, dt, inp):
        self.t += dt
        self._blink += dt
        if self.fisher:
            self.fisher.update(dt)

        if inp.key_pressed(settings.KEY_ACTION):
            self.game.fish = random_fish()
            self.game.tension = 0.2
            self.game.progress = 0.0
            from states.fighting import FightingState
            return FightingState(self.game)

        if self.t >= settings.HOOK_WINDOW:
            self.game.last_result = "lose"
            self.game.last_reason = "Demorou para fisgar!"
            self.game.last_fish = None
            from states.result import ResultState
            return ResultState(self.game)
        return self

    def draw(self, screen):
        scene.draw_world(screen)
        scene.draw_boat(screen)
        if self.game.land_point:
            scene.draw_line(screen, self.game.rod_origin, self.game.land_point)
        scene.draw_fisherman(screen, self.fisher)
        hud.draw_scoreboard(screen, self.game)

        hud.draw_text_center(screen, "FISGOU!  APERTE KEY[3]!", 150, size=46,
                             color=settings.C_RED)
        frac = 1.0 - (self.t / settings.HOOK_WINDOW)
        hud.draw_panel(screen, 240, 250, 320, 60)
        hud.draw_bar(screen, 256, 278, 288, 22, frac, settings.C_GREEN,
                     label="Janela para fisgar")

    def output(self):
        on = int(self._blink * 16) % 2 == 0
        return leds.make_output(blink_red=on, green_bits=0b1111,
                                score=self.game.score)
