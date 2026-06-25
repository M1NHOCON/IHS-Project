# 🎣 Jogo de Pesca — Projeto IHS (DE2i-150)

Jogo em **Pygame** controlado pela placa **Terasic DE2i-150** via o driver
PCIe/Character (`/dev/de2i150_dev`). Usa **apenas os periféricos embutidos**
já mapeados no FPGA: chaves (`SW`), botões (`KEY`), LEDs (`LEDR`/`LEDG`) e os
displays de 7 segmentos (`HEX0..7`).

As mecânicas da ideia original (timing, tensão, controle fino) foram
re-mapeadas sobre esses periféricos — sem alterar FPGA nem driver.

## Controles

| Ação | Na placa | No teclado (modo `--sim`) |
|---|---|---|
| Lançar / Fisgar | `KEY[3]` | `ESPAÇO` |
| Mirar / Girar o molinete (alternar) | `KEY[0]` / `KEY[1]` | `←`/`→` ou `A`/`D` |
| Dar linha (aliviar tensão) | `SW[0]` | `SHIFT` esquerdo |
| Sair | — | `ESC` |

## Saídas físicas

- **LEDR** — barra de força (mira), tensão da linha (briga) e flash da fisgada.
- **LEDG** — fase do jogo / progresso da captura.
- **HEX0..7** — pontuação total.

## Como rodar

### No laptop (desenvolvimento, sem placa)
```bash
pip install -r requirements.txt
python main.py --sim
```
No modo `--sim` aparece um **painel virtual** da placa (LEDR/LEDG/HEX) no rodapé
da tela, então dá para validar toda a lógica sem hardware.

### Na placa (DE2i-150)
```bash
# 1. carregar o driver
sudo insmod ../driver/de2i150_driver.ko
ls -l /dev/de2i150_dev

# 2. (recomendado) validar I/O e confirmar offsets antes
sudo python3 hwtest.py        # menu: SW->LEDR, sweep, ler botões, 7-seg

# 3. rodar o jogo
sudo python3 main.py --hw
```
> Acesso a `/dev/de2i150_dev` exige **root** (sudo) ou uma regra udev.

## Confirmando os offsets dos periféricos

Só `RED_LEDS = 0xC0A0` e `BUTTONS = 0xC080` estão confirmados (vêm de
`app/main.c`). Os demais (switches, green, 7-seg) são estimativas em
`settings.py` e **devem ser confirmados na placa**:

```bash
sudo python3 hwtest.py sweep   # mexa em UMA chave/botão e veja qual offset muda
```
Depois ajuste os `OFF_*` em `settings.py` (fonte única de verdade).

## Fluxo do jogo (FSM)

`MENU → AIMING → CASTING → WAITING → HOOKED → FIGHTING → RESULT → (AIMING)`

- **AIMING**: segure `KEY[0]`/`KEY[1]` para a mira; a força oscila — `KEY[3]` lança.
- **HOOKED**: na mordida, flash de LEDs + som; janela curta para `KEY[3]` (*timing*).
- **FIGHTING**: alterne `KEY[0]`↔`KEY[1]` para recolher; o peixe corre e a tensão
  sobe (`LEDR`); `SW[0]` dá linha. Estourar a tensão arrebenta; 100% captura.

## Estrutura

```
game/
  main.py            loop principal + FSM
  settings.py        offsets dos periféricos + tuning (fonte única)
  hwtest.py          smoke test de I/O na placa
  audio.py           efeitos sintetizados (sem arquivos; opcional)
  inputs.py          detecção de borda dos botões em software
  game.py            contexto compartilhado entre estados
  hardware/          base / de2i150 (real) / keyboard (sim) / factory
  states/            menu, aiming, casting, waiting, hooked, fighting, result
  entities/          fish (catálogo de peixes)
  ui/                hud (desenho) + leds (mapeamento p/ LEDR/LEDG/HEX)
```

## Notas

- **Desempenho**: o Atom N2600 é fraco — 30 FPS, gráficos simples de propósito.
- **Áudio é opcional**: se a placa não tiver saída de som, o jogo roda normal.
- **7-seg ativo-baixo**: a tabela de segmentos já trata isso (segmento aceso = 0).
