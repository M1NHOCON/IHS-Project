"""MENU: tela inicial. KEY[3] inicia."""

import settings
from states.base import State
from ui import hud, leds, scene, sprites


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.fisher = sprites.fisher_anim("idle", fps=5)

    def update(self, dt, inp):
        self.t += dt
        if self.fisher:
            self.fisher.update(dt)
        if inp.key_pressed(settings.KEY_ACTION):
            from states.aiming import AimingState
            self.game.reset_round()
            return AimingState(self.game)
        return self

    def draw(self, screen):
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)

        hud.draw_panel(screen, 180, 60, 440, 120)
        hud.draw_icon(screen, hud.ICON_ROD, 205, 78, 56)
        hud.draw_icon(screen, hud.ICON_FISH, 540, 80, 52)
        hud.draw_text_center(screen, "PESCA  IHS", 110, size=58,
                             color=settings.C_YELLOW)
        hud.draw_text_center(screen, "DE2i-150 - controle pela placa", 158,
                             size=22)

        hud.draw_panel(screen, 120, 430, 560, 150)
        lines = [
            "KEY[3] / ESPACO ....... lancar e fisgar",
            "KEY[0]/KEY[1] (A/D) ... mirar e girar o molinete",
            "SW[0] (SHIFT) ......... dar linha (aliviar tensao)",
        ]
        y = 448
        for ln in lines:
            hud.draw_text(screen, ln, 145, y, size=20)
            y += 30
        if int(self.t * 2) % 2 == 0:
            hud.draw_text_center(screen, "Pressione KEY[3] para comecar", 560,
                                 size=24, color=settings.C_YELLOW)

    def output(self):
        pos = int(self.t * 6) % 18
        out = leds.make_output(score=self.game.score)
        out.red = (1 << pos) | (1 << (17 - pos))
        out.green = 0b0001
        return out
