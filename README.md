# Projeto IHS - DE2i-150 (PCIe + Driver Linux + Jogo em Pygame)

[![Institution](https://img.shields.io/badge/Institution-UFPE-blue.svg)](https://www.ufpe.br/)
[![Department](https://img.shields.io/badge/Department-CIn-red.svg)](https://www.cin.ufpe.br/)
[![Board](https://img.shields.io/badge/Board-Terasic_DE2i--150-lightgrey.svg)](https://www.terasic.com.tw/)

Projeto final da disciplina de Introducao ao Hardware e Software (IHS), com foco em integracao de camadas:

- Hardware (FPGA Cyclone IV na DE2i-150),
- Driver Linux PCIe em kernel space (character device),
- Aplicacao user space em Python/Pygame (jogo de pesca).

## Visao geral

O repositorio esta organizado em tres frentes principais:

- `mapeamento/`: projeto Quartus/Platform Designer (Qsys) com os arquivos de hardware.
- `driver/`: driver Linux (`de2i150_driver.c`) que cria `/dev/de2i150_dev`.
- `game/`: jogo em Pygame com dois modos de execucao:
	- simulacao por teclado (`--sim`), sem placa,
	- execucao com hardware real (`--hw`), usando o driver.

## Objetivo do projeto

Disponibilizar um fluxo completo de comunicacao entre o Intel Atom da DE2i-150 e o FPGA via PCIe, e demonstrar esse fluxo com uma aplicacao interativa (jogo), que le entradas dos perifericos e escreve saidas em LEDs e displays de 7 segmentos.

## Equipe

- Paulo Messias do Nascimento - [@pmn12](https://github.com/pmn12)
- Vinicius dos Santos Felix - [@M1NHOCON](https://github.com/M1NHOCON)
- Antonio Lins Gomes de Mattos - [@linsgm](https://github.com/linsgm)
- [Membro 4 do grupo] - [@](https://github.com/Usuario)
- [Membro 5 do grupo] - [@](https://github.com/Usuario)
## Estrutura atual do repositorio

```text
IHS-Project/
	README.md
	driver/
		de2i150_driver.c
		Makefile
	game/
		main.py
		hwtest.py
		settings.py
		requirements.txt
		audio.py
		assets.py
		anim.py
		game.py
		hardware/
		states/
		ui/
		entities/
		assets/
	mapeamento/
		pcihello.qar
		pcihello_restored/
			pcihello.qpf
			pcihello.qsf
			pcihello.sof
			pcihello.v
			pcihellocore.qsys
			...
```

## Principais pastas e arquivos

- `driver/de2i150_driver.c`: driver PCIe + character device Linux.
- `driver/Makefile`: compilacao de modulo de kernel (`make`, `make clean`).
- `game/main.py`: ponto de entrada do jogo e loop principal (FSM).
- `game/hwtest.py`: teste de I/O em hardware (sem Pygame).
- `game/settings.py`: configuracoes centrais, incluindo offsets dos perifericos.
- `game/states/`: estados da FSM (`menu`, `aiming`, `casting`, `waiting`, `hooked`, `fighting`, `result`).
- `game/hardware/`: backend real (`de2i150.py`) e backend de simulacao (`keyboard.py`).
- `mapeamento/pcihello_restored/`: fontes e artefatos do projeto Quartus restaurado.

## Tecnologias e dependencias confirmadas

### Software (user space)

- Python 3
- Pygame (`game/requirements.txt`: `pygame>=2.0`)

Observacao: o audio e sintetizado no proprio codigo (sem arquivos `.wav`) e usa apenas biblioteca padrao + `pygame.mixer`.

### Kernel/driver

- C para Linux kernel module
- Infra de driver PCI (`linux/pci.h`)
- Character device (`alloc_chrdev_region`, `cdev`, `device_create`)

### Hardware

- Quartus Prime / Platform Designer (Qsys)
- Projeto em `mapeamento/` com artefatos de compilacao e restauracao

## Como preparar o ambiente

### 1. Ambiente Python (desenvolvimento local ou placa)

Na pasta `game/`:

```bash
pip install -r requirements.txt
```

### 2. Ambiente de driver (na DE2i-150/Linux)

Na pasta `driver/`:

```bash
make
```

Isso gera o modulo `de2i150_driver.ko` (se os headers do kernel corrente estiverem disponiveis em `/lib/modules/$(uname -r)/build`).

## Como executar

### Modo simulacao (sem placa)

Na pasta `game/`:

```bash
python main.py --sim
```

Tambem e aceito rodar sem argumento; em modo automatico o jogo tenta hardware real e, se nao encontrar/abrir `/dev/de2i150_dev`, cai para simulacao.

### Modo hardware real (DE2i-150)

1. Carregar o driver:

```bash
sudo insmod ../driver/de2i150_driver.ko
ls -l /dev/de2i150_dev
```

2. (Recomendado) validar I/O antes de jogar:

```bash
sudo python3 hwtest.py
```

3. Rodar o jogo com hardware:

```bash
sudo python3 main.py --hw
```

## Entradas esperadas

### Na placa

- `KEY[3]`: acao (lancar/fisgar)
- `KEY[0]` e `KEY[1]`: mirar e manivela alternada
- `SW[0]`: dar linha (aliviar tensao)

### No modo simulacao (teclado)

- Espaco: `KEY[3]`
- Esquerda/A: `KEY[0]`
- Direita/D: `KEY[1]`
- Shift esquerdo: `SW[0]`
- Esc: sair

## Saidas produzidas

- `LEDR`: barra de intensidade (forca/tensao/feedback visual)
- `LEDG`: indicacao de fase/progresso
- `HEX0..HEX7`: pontuacao
- Tela Pygame com HUD e estado atual da partida
- Em `--sim`, overlay virtual reproduzindo LEDR/LEDG/HEX

## Fluxo da aplicacao (pipeline de execucao)

O pipeline funcional identificado no codigo e:

1. Inicializa Pygame/audio/sprites.
2. Seleciona backend de hardware (`auto`, `--sim`, `--hw`).
3. Executa FSM do jogo:
	 - `MENU -> AIMING -> CASTING -> WAITING -> HOOKED -> FIGHTING -> RESULT`
4. Em cada frame:
	 - le entradas (placa ou teclado),
	 - atualiza estado,
	 - renderiza cena,
	 - escreve saidas (LEDR/LEDG/HEX).

Nao ha notebooks nem pipeline de ciencia de dados neste repositorio.

## Como interpretar os resultados

- Captura bem-sucedida: estado `RESULT` com mensagem de sucesso e incremento de pontuacao.
- Falha: perda por tempo de fisgada ou ruptura da linha (tensao maxima).
- Pontuacao acumulada aparece no HUD e nos displays de 7 segmentos (via backend).
- No modo hardware, a validacao de mapeamento de perifericos pode ser feita com `hwtest.py` (`mirror`, `sweep`, `keys`, `hex`).

## Observacoes importantes

- O driver atual implementa `read`/`write` de 32 bits com offset de arquivo como endereco relativo na BAR mapeada.
- O jogo suporta fallback automatico para simulacao quando nao consegue abrir o device real.
- O acesso a `/dev/de2i150_dev` normalmente exige `sudo` (ou regra `udev`).
- A pasta `mapeamento/` contem muitos artefatos de toolchain (inclusive arquivos restaurados e banco do Quartus).

## Limitacoes conhecidas

- Nao foram encontrados testes automatizados (unitarios/integracao) no repositorio.
- O README de `game/` e os comentarios de `settings.py` apontam incerteza/inconsistencia de offsets; existe script (`hwtest.py`) para confirmar offsets reais na placa.
- Dependencias de compilacao de kernel e ambiente Quartus nao estao automatizadas por script unico.
- O desempenho foi intencionalmente ajustado para hardware modesto (FPS padrao em 30).

## Situacao atual do projeto

Com base nos arquivos existentes, o estado atual e:

- Hardware: projeto Quartus/PCIe presente em `mapeamento/`.
- Driver: implementado em `driver/de2i150_driver.c` (nao esta apenas "em desenvolvimento").
- Aplicacao user space: implementada e executavel em `game/` (simulacao e hardware).
- Documentacao interna adicional: existe README especifico do jogo em `game/README.md`.

Quando houver divergencia entre documentacao e codigo, o codigo atual (especialmente `game/settings.py`, `game/main.py`, `game/hwtest.py` e `driver/de2i150_driver.c`) deve ser considerado a referencia principal para reproducao.
