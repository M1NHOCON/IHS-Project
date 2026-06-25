"""
FIGHTING: o nucleo do jogo (tensao + controle fino).

- Manivela: alternar KEY[0]<->KEY[1]. Cada alternancia = 1 "click" que puxa
  o peixe (progresso) mas adiciona tensao.
- O peixe "corre" aleatoriamente: a tensao sobe sozinha.
- SW[0] = dar linha: alivia a tensao, mas o peixe recua um pouco (progresso).
- Tensao estourar (>= 1) -> linha arrebenta (perdeu).
- Progresso chegar a 1 -> peixe capturado (ganhou).
"""

import random

import pygame

import audio
import settings
from states.base import State
from ui import hud, leds


class FightingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.last_side = None        # 'L' ou 'R' da ultima manivela
        self.run_timer = 0.0         # >0 enquanto o peixe corre
        self.shake = 0.0

    def update(self, dt, inp):
        g = self.game
        fish = g.fish
        give_line = inp.switch_on(settings.SW_GIVE_LINE)

        # --- peixe corre? ---
        if self.run_timer > 0:
            self.run_timer -= dt
            g.tension += fish.run_power * dt
            self.shake = 6.0
        else:
            if random.random() < fish.run_chance * dt:
                self.run_timer = random.uniform(0.4, 0.9)

        # --- dissipacao natural da tensao ---
        g.tension -= settings.TENSION_DECAY * dt

        # --- manivela (so se NAO estiver dando linha) ---
        if not give_line:
            clicked = False
            if inp.key_pressed(settings.KEY_LEFT) and self.last_side != 'L':
                self.last_side = 'L'
                clicked = True
            elif inp.key_pressed(settings.KEY_RIGHT) and self.last_side != 'R':
                self.last_side = 'R'
                clicked = True
            if clicked:
                g.progress += settings.REEL_GAIN * fish.reel_factor
                g.tension += settings.TENSION_PER_REEL
                audio.play("reel")

        # --- dar linha ---
        if give_line:
            g.tension -= settings.GIVE_LINE_RELIEF * dt
            g.progress -= settings.GIVE_LINE_PROGRESS_DRAIN * dt

        # --- limites ---
        g.tension = max(0.0, g.tension)
        g.progress = max(0.0, g.progress)
        self.shake = max(0.0, self.shake - dt * 20)

        # --- condicoes de fim ---
        if g.tension >= settings.TENSION_MAX:
            audio.play("snap")
            g.last_result = "lose"
            g.last_reason = "A linha arrebentou!"
            g.last_fish = fish
            from states.result import ResultState
            return ResultState(self.game)

        if g.progress >= settings.PROGRESS_WIN:
            audio.play("catch")
            g.last_result = "win"
            g.last_reason = ""
            g.last_fish = fish
            g.score += fish.points
            g.fish_caught += 1
            from states.result import ResultState
            return ResultState(self.game)

        return self

    def draw(self, screen):
        g = self.game
        fish = g.fish
        hud.draw_scene(screen)
        hud.draw_boat(screen, g.boat_x)

        # peixe vai do ponto de queda em direcao ao barco conforme progresso
        lp = g.land_point or (600, hud.WATER_Y + 80)
        fx = lp[0] + (g.boat_x - lp[0]) * g.progress
        fy = hud.WATER_Y + 70 + random.uniform(-self.shake, self.shake)
        pygame.draw.line(screen, settings.C_WHITE, g.rod_origin, (fx, fy), 1)
        self._draw_fish(screen, fx, fy, fish.color, fish.size)

        # barras
        hud.draw_bar(screen, 250, 30, 300, 24, g.tension, settings.C_GREEN,
                     label="Tensao da linha", danger=True)
        hud.draw_bar(screen, 250, 90, 300, 24, g.progress, settings.C_YELLOW,
                     label="Progresso")
        hud.draw_text(screen, "Peixe: %s (vale %d)" % (fish.name, fish.points),
                      250, 130, size=18)
        hud.draw_text_center(screen,
                             "Alterne KEY[0]/KEY[1] para recolher  |  "
                             "SW[0] = dar linha", 250, size=20)

    def _draw_fish(self, screen, x, y, color, size):
        r = 6 + size * 2
        pygame.draw.ellipse(screen, color, (x - r, y - r // 2, r * 2, r))
        # cauda
        pygame.draw.polygon(screen, color,
                            [(x + r, y), (x + r + 10, y - 8), (x + r + 10, y + 8)])

    def output(self):
        g = self.game
        # LEDR = tensao (vira "perigo" quando cheia); LEDG = progresso em 4 niveis
        green = (1 << int(g.progress * 4)) - 1 if g.progress > 0 else 0
        return leds.make_output(red_value=g.tension,
                                green_bits=green & 0xF,
                                score=g.score)
