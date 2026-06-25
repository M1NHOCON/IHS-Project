"""
Audio totalmente opcional e auto-contido.

Em vez de depender de arquivos .wav, sintetizamos beeps simples em memoria
com o modulo 'array' (sem numpy). Se a placa nao tiver dispositivo de audio,
nada disso quebra o jogo: todas as falhas viram no-op.
"""

import math
from array import array

import pygame

_MIXER_HZ = 22050
_enabled = False
_sounds = {}


def init():
    """Inicializa o mixer e pre-sintetiza os efeitos. Silencioso em falha."""
    global _enabled
    try:
        pygame.mixer.pre_init(_MIXER_HZ, -16, 1)  # mono, 16 bits
        pygame.mixer.init()
        _enabled = True
    except pygame.error:
        _enabled = False
        return

    # nome -> (frequencia Hz, duracao s, forma)
    _sounds["bite"]  = _tone(880, 0.12, "square")
    _sounds["hook"]  = _chirp(400, 1200, 0.18)
    _sounds["reel"]  = _tone(220, 0.05, "square", vol=0.4)
    _sounds["snap"]  = _noise(0.25)
    _sounds["catch"] = _arpeggio([523, 659, 784, 1047], 0.09)
    _sounds["splash"] = _tone(160, 0.15, "sine", vol=0.5)


def play(name: str):
    if not _enabled:
        return
    snd = _sounds.get(name)
    if snd is not None:
        try:
            snd.play()
        except pygame.error:
            pass


# ---------------------------------------------------------------------------
# Sintese
# ---------------------------------------------------------------------------
def _make_sound(samples):
    buf = array("h", samples)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _tone(freq, dur, shape="sine", vol=0.6):
    n = int(_MIXER_HZ * dur)
    amp = int(32767 * vol)
    out = []
    for i in range(n):
        t = i / _MIXER_HZ
        if shape == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        env = _envelope(i, n)
        out.append(int(amp * v * env))
    return _make_sound(out)


def _chirp(f0, f1, dur, vol=0.6):
    n = int(_MIXER_HZ * dur)
    amp = int(32767 * vol)
    out = []
    for i in range(n):
        t = i / _MIXER_HZ
        f = f0 + (f1 - f0) * (i / n)
        v = math.sin(2 * math.pi * f * t)
        out.append(int(amp * v * _envelope(i, n)))
    return _make_sound(out)


def _arpeggio(freqs, step, vol=0.6):
    out = []
    for f in freqs:
        n = int(_MIXER_HZ * step)
        amp = int(32767 * vol)
        for i in range(n):
            t = i / _MIXER_HZ
            v = math.sin(2 * math.pi * f * t)
            out.append(int(amp * v * _envelope(i, n)))
    return _make_sound(out)


def _noise(dur, vol=0.5):
    import random
    n = int(_MIXER_HZ * dur)
    amp = int(32767 * vol)
    out = [int(amp * (random.random() * 2 - 1) * _envelope(i, n))
           for i in range(n)]
    return _make_sound(out)


def _envelope(i, n):
    """Fade in/out curto para evitar estalos."""
    edge = max(1, n // 16)
    if i < edge:
        return i / edge
    if i > n - edge:
        return (n - i) / edge
    return 1.0
