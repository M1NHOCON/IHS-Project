"""
FIGHTING: o nucleo do jogo (tensao + controle fino).

- Manivela: alternar KEY[0]<->KEY[1]. Cada alternancia = 1 "click" que puxa
  o peixe (progresso) mas adiciona tensao.
- O peixe "corre" aleatoriamente: a tensao sobe sozinha.
- SW[0] = dar linha: alivia a tensao, mas o peixe recua (progresso).
- Tensao estourar (>= 1) -> linha arrebenta (perdeu).
- Progresso chegar a 1 -> peixe capturado (ganhou).
"""

import random

import audio
import settings
from states.base import State
from ui import hud, leds, scene, sprites


class FightingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.last_side = None
        self.run_timer = 0.0
        self.shake = 0.0
        self.fisher = sprites.fisher_anim("fish", fps=8)

    def update(self, dt, inp):
        g = self.game
        fish = g.fish
        give_line = inp.switch_on(settings.SW_GIVE_LINE)
        if self.fisher:
            self.fisher.update(dt)

        # peixe corre?
        if self.run_timer > 0:
            self.run_timer -= dt
            g.tension += fish.run_power * dt
            self.shake = 6.0
        elif random.random() < fish.run_chance * dt:
            self.run_timer = random.uniform(0.4, 0.9)

        # dissipacao natural
        g.tension -= settings.TENSION_DECAY * dt

        # manivela (so se NAO estiver dando linha)
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

        # dar linha
        if give_line:
            g.tension -= settings.GIVE_LINE_RELIEF * dt
            g.progress -= settings.GIVE_LINE_PROGRESS_DRAIN * dt

        g.tension = max(0.0, g.tension)
        g.progress = max(0.0, g.progress)
        self.shake = max(0.0, self.shake - dt * 20)

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

    def _creature_pos(self):
        g = self.game
        start = g.land_point or (640, scene.WATER_Y + 80)
        end = (g.rod_origin[0] - 10, scene.WATER_Y + 46)
        fx = start[0] + (end[0] - start[0]) * g.progress
        fy = start[1] + (end[1] - start[1]) * g.progress
        fy += random.uniform(-self.shake, self.shake)
        return fx, fy

    def draw(self, screen):
        g = self.game
        scene.draw_world(screen)
        scene.draw_boat(screen)
        scene.draw_fisherman(screen, self.fisher)

        pos = self._creature_pos()
        scene.draw_line(screen, g.rod_origin, pos)
        scene.draw_catch(screen, g.fish, pos, flip=True)

        hud.draw_scoreboard(screen, g)
        hud.draw_panel(screen, 240, 20, 320, 96)
        hud.draw_bar(screen, 256, 48, 288, 20, g.tension, settings.C_GREEN,
                     label="Tensao da linha", danger=True)
        hud.draw_bar(screen, 256, 94, 288, 20, g.progress, settings.C_YELLOW,
                     label="Progresso: %s (vale %d)" % (g.fish.name, g.fish.points))
        hud.draw_text_center(screen,
                             "Alterne KEY[0]/KEY[1]  |  SW[0] = dar linha",
                             570, size=20, color=settings.C_YELLOW)

    def output(self):
        g = self.game
        green = (1 << int(g.progress * 4)) - 1 if g.progress > 0 else 0
        return leds.make_output(red_value=g.tension,
                                green_bits=green & 0xF,
                                score=g.score)
