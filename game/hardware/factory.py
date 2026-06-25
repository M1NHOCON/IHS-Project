"""
Escolhe o backend de hardware.

  --hw   forca o FPGA real (/dev/de2i150_dev)
  --sim  forca o teclado/tela
  (nada) auto: tenta o real; se /dev nao existir ou faltar permissao,
         cai para o sim e avisa.
"""

import os

import settings
from hardware.keyboard import KeyboardBackend


def make_backend(mode: str = "auto"):
    """mode in {"hw", "sim", "auto"} -> (backend, usou_real: bool)."""
    if mode == "sim":
        return KeyboardBackend(), False

    if mode == "hw":
        from hardware.de2i150 import De2i150Backend
        return De2i150Backend(), True

    # auto
    if os.path.exists(settings.DEVICE_PATH):
        try:
            from hardware.de2i150 import De2i150Backend
            return De2i150Backend(), True
        except OSError as e:
            print("[hardware] %s existe mas nao abriu (%s). "
                  "Use sudo ou regra udev. Caindo para --sim." %
                  (settings.DEVICE_PATH, e))
    else:
        print("[hardware] %s nao encontrado. Rodando em modo --sim." %
              settings.DEVICE_PATH)
    return KeyboardBackend(), False
