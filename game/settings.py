"""
Configuracoes centrais do Jogo de Pesca (Projeto IHS - DE2i-150).

Tudo que e "constante de tuning" ou "endereco de periferico" mora aqui,
para ter uma unica fonte de verdade.
"""

# ----------------------------------------------------------------------------
# Tela / loop
# ----------------------------------------------------------------------------
SCREEN_W = 800
SCREEN_H = 600
FPS = 30                     # Atom N2600 e fraco: manter leve.
TITLE = "Pesca IHS - DE2i-150"

# ----------------------------------------------------------------------------
# Dispositivo de caractere exposto pelo driver PCIe
# ----------------------------------------------------------------------------
DEVICE_PATH = "/dev/de2i150_dev"

# ----------------------------------------------------------------------------
# OFFSETS dos perifericos (PIO Avalon de 32 bits).
#
# CONFIRMADOS em app/main.c (ja testados na placa):
#   RED_LEDS = 0xC0A0   |   BUTTONS (KEY) = 0xC080
#
# Os demais foram estimados a partir do espacamento de 0x20 entre PIOs no
# pcihellocore.sopcinfo. DEVEM ser confirmados na placa com game/hwtest.py
# antes de confiar 100%. No modo --sim nada disso e usado.
# ----------------------------------------------------------------------------
OFF_BUTTONS    = 0xC080     # KEY[3:0]  (CONFIRMADO) - ja invertido no HW (1 = pressionado)
OFF_RED_LEDS   = 0xC0A0     # LEDR[17:0] (CONFIRMADO)
OFF_SWITCHES   = 0xC060     # SW[17:0]   (CONFIRMAR)
OFF_GREEN_LEDS = 0xC0C0     # LEDG[3:0]  (CONFIRMAR)
OFF_HEX_0_3    = 0xC000     # HEX0..HEX3 empacotados (CONFIRMAR)
OFF_HEX_4_5    = 0xC040     # HEX4..HEX5 empacotados (CONFIRMAR)
OFF_HEX_6_7    = 0xC020     # HEX6..HEX7 empacotados (CONFIRMAR)

# Faixa varrida pelo hwtest.py ao procurar os offsets.
HWTEST_SWEEP = [0xC000, 0xC020, 0xC040, 0xC060, 0xC080,
                0xC0A0, 0xC0C0, 0xC0E0, 0xC100, 0xC120]

# ----------------------------------------------------------------------------
# Mapeamento de controles -> indices logicos
#
# KEY[3] = acao (lancar / fisgar)
# KEY[0] / KEY[1] = mira fina e manivela (alternar = recolher molinete)
# SW[0]  = "dar linha" (alivio de tensao de emergencia)
# ----------------------------------------------------------------------------
KEY_ACTION = 3
KEY_LEFT   = 0
KEY_RIGHT  = 1
KEY_EXTRA  = 2
SW_GIVE_LINE = 0

# ----------------------------------------------------------------------------
# Teclado (modo --sim): tecla pygame -> controle logico.
# Preenchido em hardware/keyboard.py (importa pygame la, nao aqui).
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Tuning de jogabilidade
# ----------------------------------------------------------------------------
AIM_MIN_DEG = 20.0          # mira: limites do angulo de lancamento
AIM_MAX_DEG = 160.0
AIM_SPEED   = 60.0          # graus/seg ao segurar KEY[0]/KEY[1]

POWER_SPEED = 1.6           # velocidade do oscilador de forca (ciclos/seg)

WAIT_MIN = 1.5              # espera (seg) ate o peixe morder
WAIT_MAX = 5.0

HOOK_WINDOW = 0.9           # janela (seg) para fisgar apos a mordida

# Briga (FIGHTING)
REEL_GAIN      = 0.06       # progresso ganho por "click" de manivela
TENSION_PER_REEL = 0.05     # tensao adicionada por click de manivela
TENSION_DECAY  = 0.25       # tensao dissipada por seg quando nao se recolhe
GIVE_LINE_RELIEF = 0.9      # tensao dissipada por seg ao "dar linha" (SW0)
GIVE_LINE_PROGRESS_DRAIN = 0.04  # progresso perdido por seg ao dar linha
TENSION_MAX    = 1.0        # acima disso a linha arrebenta
PROGRESS_WIN   = 1.0        # progresso para capturar

# ----------------------------------------------------------------------------
# Cores (RGB)
# ----------------------------------------------------------------------------
C_SKY      = (135, 206, 235)
C_WATER    = (28, 107, 160)
C_WATER_DK = (18, 78, 120)
C_WHITE    = (245, 245, 245)
C_BLACK    = (15, 15, 20)
C_YELLOW   = (245, 205, 60)
C_RED      = (220, 60, 60)
C_GREEN    = (70, 200, 110)
C_LED_OFF  = (60, 60, 60)
C_PANEL    = (25, 28, 34)
