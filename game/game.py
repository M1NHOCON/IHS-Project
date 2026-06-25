"""
Contexto compartilhado entre os estados da FSM.

Guarda o que precisa sobreviver a troca de estados: pontuacao, peixe atual,
ponto onde a isca caiu, posicao do barco, etc.
"""

from ui import scene


class Game:
    def __init__(self):
        self.boat_x = scene.BOAT_X
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
        self.aim_x = scene.BOAT_X + 320     # marcador de mira na agua
        self.power = 0.0
        self.land_target = None     # (x, y) alvo escolhido na mira
        self.land_point = None      # (x, y) onde a isca caiu de fato
        self.fish = None
        self.tension = 0.0
        self.progress = 0.0

    @property
    def rod_origin(self):
        return scene.rod_origin(self)
