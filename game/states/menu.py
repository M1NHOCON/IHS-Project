"""MENU: tela inicial. KEY[3] inicia."""

import settings
from states.base import State
from ui import hud, leds


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0

    def update(self, dt, inp):
        self.t += dt
        if inp.key_pressed(settings.KEY_ACTION):
            from states.aiming import AimingState
            self.game.reset_round()
            return AimingState(self.game)
        return self

    def draw(self, screen):
        hud.draw_scene(screen)
        hud.draw_boat(screen, self.game.boat_x)
        hud.draw_text_center(screen, "PESCA  IHS", 110, size=64,
                             color=settings.C_BLACK)
        hud.draw_text_center(screen, "DE2i-150  -  controle pela placa", 160,
                             size=24)

        lines = [
            "KEY[3] / ESPACO ....... lancar e fisgar",
            "KEY[0]/KEY[1] (A/D) ... mirar e girar o molinete (alternar)",
            "SW[0] (SHIFT) ......... dar linha (aliviar tensao)",
            "",
            "Pressione KEY[3] para comecar",
        ]
        y = 360
        for ln in lines:
            hud.draw_text_center(screen, ln, y, size=22, bold=False)
            y += 34

    def output(self):
        # marquee suave nos LEDR enquanto no menu
        pos = int(self.t * 6) % 18
        out = leds.make_output(score=self.game.score)
        out.red = (1 << pos) | (1 << (17 - pos))
        out.green = 0b0001
        return out
