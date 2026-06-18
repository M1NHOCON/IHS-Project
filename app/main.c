#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>      
#include <unistd.h>     
#include <stdint.h>     

#define RED_LEDS_OFFSET 0xC0A0
#define BUTTONS_OFFSET  0xC080

int main() {
    int fd = open("/dev/de2i150_dev", O_RDWR);
    if (fd < 0) {
        perror("Falha ao abrir o dispositivo");
        return -1;
    }

    printf("Efeito Bolinha com Play/Pause!\n");
    printf("Pressione o 1o botao (KEY0) na placa para pausar ou continuar.\n");
    printf("Pressione Ctrl+C no terminal para encerrar.\n");

    uint32_t led_val;
    uint32_t botoes;
    
    int num_leds = 18;
    int tempo_espera = 50000; // 50 milissegundos
    
    // Variáveis de estado da bolinha
    int posicao = 0;
    int direcao = 1; // 1 = Direita para Esquerda, -1 = Esquerda para Direita
    
    // Variáveis de estado do botão
    int pausado = 0;         // 0 = Rodando, 1 = Pausado
    int estado_anterior = 1; // O botão solto envia 1 (Active-Low)

    // Loop principal (Roda a cada 50ms)
    while (1) {
        
        // 1. LÊ O ESTADO DOS BOTÕES
        pread(fd, &botoes, sizeof(uint32_t), BUTTONS_OFFSET);
        
        // Pega apenas o bit 0 (que corresponde ao KEY0)
        int estado_atual = botoes & 0x01;

        // 2. DETECTA O CLIQUE (Borda de Descida)
        // Só alterna o estado se o botão foi APERTADO AGORA (antes era 1, agora é 0)
        if (estado_atual == 0 && estado_anterior == 1) {
            pausado = !pausado; // Alterna entre 0 e 1
            if (pausado) {
                printf("Bolinha PAUSADA.\n");
            } else {
                printf("Bolinha RODANDO.\n");
            }
        }
        estado_anterior = estado_atual; // Salva o estado para a próxima rodada

        // 3. ATUALIZA OS LEDS (Só se não estiver pausado)
        if (!pausado) {
            // Acende o LED na posição atual
            led_val = 1 << posicao;
            pwrite(fd, &led_val, sizeof(uint32_t), RED_LEDS_OFFSET);

            // Calcula a próxima posição
            posicao += direcao;

            // Bateu na parede da esquerda? Inverte a direção
            if (posicao >= num_leds - 1) {
                posicao = num_leds - 1;
                direcao = -1;
            } 
            // Bateu na parede da direita? Inverte a direção
            else if (posicao <= 0) {
                posicao = 0;
                direcao = 1;
            }
        }

        // 4. PAUSA DO QUADRO (Dita a velocidade da bolinha e serve como "debounce" do botão)
        usleep(tempo_espera);
    }

    close(fd);
    return 0;
}