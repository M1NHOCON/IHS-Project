"""
Contexto compartilhado entre os estados da FSM.

Guarda o que precisa sobreviver a troca de estados: pontuacao, peixe atual,
ponto onde a isca caiu, posicao do barco, etc.
"""

from ui import hud


class Game:
    def __init__(self):
        self.boat_x = 120
        self.reset_round()
        # placar acumulado
        self.score = 0
        self.fish_caught = 0
        # ultima mensagem de resultado
        self.last_result = ""       # "win" | "lose"
        self.last_reason = ""
        self.last_fish = None

    def reset_round(self):
        """Limpa o estado de uma rodada (um lance)."""
        self.aim_angle = 90.0
        self.power = 0.0
        self.land_point = None      # (x, y) onde a isca caiu
        self.fish = None
        self.tension = 0.0
        self.progress = 0.0

    @property
    def rod_origin(self):
        return hud.rod_tip(self.boat_x)
