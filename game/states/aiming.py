"""
AIMING: mira o ponto onde a linha vai cair.

KEY[0]/KEY[1] deslizam o marcador na agua (perto/longe). A barra de FORCA
oscila (timing): quanto mais cheia no lance, mais perto do alvo a isca chega.
KEY[3] lanca.
"""

import settings
from states.base import State
from ui import hud, leds, scene, sprites


class AimingState(State):
    def __init__(self, game):
        super().__init__(game)
        self._power_dir = 1.0
        self.fisher = sprites.fisher_anim("fish", fps=6)
        self.min_x = scene.BOAT_X + settings.CAST_NEAR
        self.max_x = settings.SCREEN_W - settings.CAST_MARGIN
        # garante que o alvo comeca dentro dos limites
        game.aim_x = min(self.max_x, max(self.min_x, game.aim_x))

    def update(self, dt, inp):
        g = self.game
        if self.fisher:
            self.fisher.update(dt)

        # marcador de mira: esquerda = mais perto, direita = mais longe
        if inp.key_down(settings.KEY_LEFT):
            g.aim_x -= settings.AIM_SPEED_PX * dt
        if inp.key_down(settings.KEY_RIGHT):
            g.aim_x += settings.AIM_SPEED_PX * dt
        g.aim_x = min(self.max_x, max(self.min_x, g.aim_x))

        # forca oscila (timing do lance)
        g.power += self._power_dir * settings.POWER_SPEED * dt
        if g.power >= 1.0:
            g.power = 1.0
            self._power_dir = -1.0
        elif g.power <= 0.0:
            g.power = 0.0
            self._power_dir = 1.0

        if inp.key_pressed(settings.KEY_ACTION):
            # alcance atingido = fracao do caminho ate o alvo, conforme a forca
            frac = settings.CAST_MIN_FRACTION + \
                (1.0 - settings.CAST_MIN_FRACTION) * g.power
            reach_x = self.min_x + (g.aim_x - self.min_x) * frac
            g.land_target = (reach_x, scene.WATER_Y + 8)
            from states.casting import CastingState
            return CastingState(self.game)
        return self

    def draw(self, screen):
        g = self.game
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)
        hud.draw_scoreboard(screen, g)

        # linha de mira ate o alvo na agua + marcador
        target = (g.aim_x, scene.WATER_Y + 8)
        hud.draw_target_line(screen, g.rod_origin, target)

        hud.draw_panel(screen, 250, 24, 300, 50)
        hud.draw_bar(screen, 266, 44, 268, 20, g.power, settings.C_YELLOW,
                     label="Forca do arremesso")
        hud.draw_text_center(screen, "Mire com KEY[0]/KEY[1] - KEY[3] LANCA",
                             120, size=26, color=settings.C_YELLOW)

    def output(self):
        return leds.make_output(red_value=self.game.power,
                                green_bits=0b0011,
                                score=self.game.score)
