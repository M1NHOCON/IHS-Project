"""AIMING: mira fina (KEY0/KEY1) + barra de forca oscilante. KEY[3] lanca."""

import settings
from states.base import State
from ui import hud, leds


class AimingState(State):
    def __init__(self, game):
        super().__init__(game)
        self._power_dir = 1.0          # oscilador triangular 0..1

    def update(self, dt, inp):
        g = self.game

        # mira fina: segurar KEY0 = sobe angulo, KEY1 = desce
        if inp.key_down(settings.KEY_LEFT):
            g.aim_angle += settings.AIM_SPEED * dt
        if inp.key_down(settings.KEY_RIGHT):
            g.aim_angle -= settings.AIM_SPEED * dt
        g.aim_angle = max(settings.AIM_MIN_DEG,
                          min(settings.AIM_MAX_DEG, g.aim_angle))

        # forca oscila sozinha (timing do lance)
        g.power += self._power_dir * settings.POWER_SPEED * dt
        if g.power >= 1.0:
            g.power = 1.0
            self._power_dir = -1.0
        elif g.power <= 0.0:
            g.power = 0.0
            self._power_dir = 1.0

        if inp.key_pressed(settings.KEY_ACTION):
            from states.casting import CastingState
            return CastingState(self.game)
        return self

    def draw(self, screen):
        g = self.game
        hud.draw_scene(screen)
        hud.draw_boat(screen, g.boat_x)
        hud.draw_aim(screen, g.rod_origin, g.aim_angle)
        hud.draw_bar(screen, 280, 40, 240, 22, g.power, settings.C_YELLOW,
                     label="Forca do lancamento")
        hud.draw_text(screen, "Mira: %d deg" % int(g.aim_angle), 280, 76,
                      size=18)
        hud.draw_text_center(screen, "KEY[3] para LANCAR", 250, size=26)

    def output(self):
        # LEDR mostra a forca; LEDG indica fase "mira"
        return leds.make_output(red_value=self.game.power,
                                green_bits=0b0011,
                                score=self.game.score)
