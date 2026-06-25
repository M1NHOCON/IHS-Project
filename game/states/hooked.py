"""
HOOKED: a mordida! "FISGOU!" com flash de LEDs + som.
Janela curta para KEY[3] fisgar (timing). Errar = peixe foge.
"""

import audio
import settings
from entities.fish import random_fish
from states.base import State
from ui import hud, leds


class HookedState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self._blink = 0.0

    def enter(self):
        audio.play("hook")

    def update(self, dt, inp):
        self.t += dt
        self._blink += dt

        if inp.key_pressed(settings.KEY_ACTION):
            # fisgou a tempo -> sorteia o peixe e vai para a briga
            self.game.fish = random_fish()
            self.game.tension = 0.2
            self.game.progress = 0.0
            from states.fighting import FightingState
            return FightingState(self.game)

        if self.t >= settings.HOOK_WINDOW:
            # demorou: peixe escapou
            self.game.last_result = "lose"
            self.game.last_reason = "Demorou para fisgar!"
            self.game.last_fish = None
            from states.result import ResultState
            return ResultState(self.game)
        return self

    def draw(self, screen):
        hud.draw_scene(screen)
        hud.draw_boat(screen, self.game.boat_x)
        hud.draw_text_center(screen, "FISGOU!  APERTE KEY[3]!", 220, size=48,
                             color=settings.C_RED)
        # barra do tempo restante
        frac = 1.0 - (self.t / settings.HOOK_WINDOW)
        hud.draw_bar(screen, 250, 300, 300, 26, frac, settings.C_GREEN,
                     label="Janela para fisgar")

    def output(self):
        # flash forte: pisca todos os LEDR rapidamente
        on = int(self._blink * 16) % 2 == 0
        out = leds.make_output(blink_red=on, green_bits=0b1111,
                               score=self.game.score)
        return out
