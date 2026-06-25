"""RESULT: mostra captura/perda e volta para AIMING ao pressionar KEY[3]."""

import settings
from states.base import State
from ui import hud, leds


class ResultState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0

    def update(self, dt, inp):
        self.t += dt
        # pequeno atraso para evitar pular por causa do mesmo aperto
        if self.t > 0.4 and inp.key_pressed(settings.KEY_ACTION):
            from states.aiming import AimingState
            self.game.reset_round()
            return AimingState(self.game)
        return self

    def draw(self, screen):
        g = self.game
        hud.draw_scene(screen)
        hud.draw_boat(screen, g.boat_x)

        if g.last_result == "win":
            f = g.last_fish
            hud.draw_text_center(screen, "CAPTUROU!", 150, size=56,
                                 color=settings.C_GREEN)
            if f:
                hud.draw_text_center(screen,
                                     "%s  +%d pontos" % (f.name, f.points),
                                     220, size=30)
        else:
            hud.draw_text_center(screen, "PERDEU...", 150, size=56,
                                 color=settings.C_RED)
            hud.draw_text_center(screen, g.last_reason, 220, size=28)

        hud.draw_text_center(screen,
                             "Total: %d pontos  |  %d peixes" %
                             (g.score, g.fish_caught), 300, size=26)
        hud.draw_text_center(screen, "KEY[3] para pescar de novo", 400,
                             size=24)

    def output(self):
        green = 0b1111 if self.game.last_result == "win" else 0b0000
        red = 0.0 if self.game.last_result == "win" else 1.0
        return leds.make_output(red_value=red, green_bits=green,
                                score=self.game.score)
