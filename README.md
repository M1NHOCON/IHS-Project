# Projeto IHS - Comunicação PCIe com DE2i-150 🚀

[![Institution](https://img.shields.io/badge/Institution-UFPE-blue.svg)](https://www.ufpe.br/)
[![Department](https://img.shields.io/badge/Department-CIn-red.svg)](https://www.cin.ufpe.br/)
[![Board](https://img.shields.io/badge/Board-Terasic_DE2i--150-lightgrey.svg)](https://www.terasic.com.tw/)

Projeto final da disciplina de **Introdução ao Hardware e Software (IHS)** do curso de Engenharia da Computação no Centro de Informática (CIn) da UFPE.

O objetivo deste projeto é criar uma aplicação full-stack (Hardware + Kernel + User Space) rodando em ambiente Linux (Yocto/Lubuntu) utilizando o processador Intel Atom N2600 para se comunicar com o FPGA Altera Cyclone IV através do barramento PCI Express (PCIe).

## 👥 Equipe
* **Paulo Messias do Nascimento** - [@pmn12](https://github.com/pmn12)
* **Vinicius dos Santos Felix** - [@M1NHOCON](https://github.com/M1NHOCON)
* **[Nome do Membro 3]** - [@Usuario2](https://github.com/Usuario2)
---

## 🎯 Tema da Aplicação
*(Escreva aqui um breve resumo do que a aplicação de vocês faz. Ex: Um jogo de reflexos, um controlador de acesso, um simulador de algo, etc. Como o tema é livre, caprichem na descrição!)*

---

## 🛠️ Arquitetura do Projeto

O projeto é dividido em três camadas principais:

### 1. Hardware (FPGA - Cyclone IV)
Mapeamento dos periféricos da placa utilizando o **Platform Designer (Qsys)** e **Verilog** no Quartus Prime 17.1. Os seguintes componentes foram mapeados via blocos PIO (Parallel I/O) de 32 bits para acesso via memória:
* 🎛️ **Displays de 7 Segmentos** (`HEX0` a `HEX7`)
* 🔴 **LEDs Vermelhos** (`LEDR[17:0]`)
* 🟢 **LEDs Verdes** (`LEDG[8:0]`)
* 🕹️ **Chaves Deslizantes** (`SW[17:0]`)
* 🔘 **Botões de Pressão** (`KEY[3:0]`)
* ❄️ **Controle do Cooler** (`FAN_CTRL`) - *Configurado para iniciar ligado por segurança.*

### 2. Kernel Space (Driver PCIe)
*(Em desenvolvimento)* - Desenvolvimento de um *Character Device Driver* em C para o Linux. O driver será responsável por:
* Reconhecer o dispositivo Altera no barramento PCIe.
* Mapear os endereços físicos (I/O Memory) do FPGA para o espaço virtual do kernel (`ioremap`).
* Expor as funcionalidades de leitura e escrita para o User Space através de arquivos em `/dev/`.

### 3. User Space (Aplicação)
*(Em desenvolvimento)* - Aplicação final escrita em C/C++ que interage com o driver para criar a lógica de negócio e a interface com o usuário.

---

## 🚀 Como Executar

### Pré-requisitos
* **Quartus Prime 17.1** (Para síntese de hardware)
* **Placa Terasic DE2i-150**
* Sistema Operacional Linux rodando no Intel Atom da placa.

### Passo 1: Programando o Hardware
1. Abra o projeto no Quartus Prime 17.1.
2. Compile o projeto (`Ctrl + L`).
3. Conecte o cabo USB-Blaster na placa.
4. Vá em *Tools -> Programmer*, selecione o arquivo `output_files/pcihello.sof` e clique em *Start*.

### Passo 2: Validando o PCIe
Com a placa programada, reinicie o sistema (botão Reset) para que a BIOS reconheça o hardware. No terminal do Linux da placa, execute:
```bash
lspci | grep Altera
