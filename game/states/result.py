"""RESULT: mostra captura/perda e volta para AIMING ao pressionar KEY[3]."""

import settings
from states.base import State
from ui import hud, leds, scene, sprites


class ResultState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.fisher = sprites.fisher_anim("idle", fps=5)

    def update(self, dt, inp):
        self.t += dt
        if self.fisher:
            self.fisher.update(dt)
        if self.t > 0.4 and inp.key_pressed(settings.KEY_ACTION):
            from states.aiming import AimingState
            self.game.reset_round()
            return AimingState(self.game)
        return self

    def _title(self):
        g = self.game
        if g.last_result != "win":
            return "PERDEU...", settings.C_RED
        kind = g.last_fish.kind if g.last_fish else "fish"
        if kind == "treasure":
            return "TESOURO!", settings.C_YELLOW
        if kind == "junk":
            return "SO LIXO...", settings.C_WHITE
        return "CAPTUROU!", settings.C_GREEN

    def draw(self, screen):
        g = self.game
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)

        title, color = self._title()
        hud.draw_panel(screen, 210, 90, 380, 140)
        if g.last_result == "win" and g.last_fish:
            f = g.last_fish
            if f.kind != "junk":
                hud.draw_icon(screen, hud.ICON_TROPHY, 232, 110, 40)
            hud.draw_text_center(screen, title, 130, size=50, color=color)
            hud.draw_text_center(screen, "%s  +%d pts" % (f.name, f.points),
                                 188, size=28)
            # mostra o que pescou, grande, no centro
            scene.draw_catch(screen, f, (settings.SCREEN_W // 2, 300),
                             flip=False, wiggle=False)
        else:
            hud.draw_text_center(screen, title, 130, size=50, color=color)
            hud.draw_text_center(screen, g.last_reason, 188, size=26)

        hud.draw_scoreboard(screen, g)
        hud.draw_panel(screen, 230, 470, 340, 90)
        hud.draw_text_center(screen,
                             "Total: %d pts  |  %d peixes" %
                             (g.score, g.fish_caught), 498, size=24)
        if int(self.t * 2) % 2 == 0:
            hud.draw_text_center(screen, "KEY[3] para pescar de novo", 536,
                                 size=22, color=settings.C_YELLOW)

    def output(self):
        green = 0b1111 if self.game.last_result == "win" else 0b0000
        red = 0.0 if self.game.last_result == "win" else 1.0
        return leds.make_output(red_value=red, green_bits=green,
                                score=self.game.score)
