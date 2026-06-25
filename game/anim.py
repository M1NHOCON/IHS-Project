"""Animacao simples baseada em lista de frames (Surfaces do pygame)."""


class Animation:
    def __init__(self, frames, fps=8, loop=True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.t = 0.0
        self.i = 0
        self.done = False

    def reset(self):
        self.t = 0.0
        self.i = 0
        self.done = False
        return self

    def update(self, dt):
        if self.done or not self.frames:
            return
        self.t += dt
        adv = int(self.t * self.fps)
        n = len(self.frames)
        if self.loop:
            self.i = adv % n
        else:
            if adv >= n:
                self.i = n - 1
                self.done = True
            else:
                self.i = adv

    def image(self):
        return self.frames[self.i] if self.frames else None
