"""
Estado base da FSM.

Cada estado: update(dt, inp) -> proximo estado (ou self), draw(screen),
output() -> OutputState (LEDs/HEX). O loop principal chama enter() quando
ocorre uma troca de estado.
"""

from hardware.base import OutputState


class State:
    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def update(self, dt, inp):
        return self

    def draw(self, screen):
        pass

    def output(self) -> OutputState:
        return OutputState()
