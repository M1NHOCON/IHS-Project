#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>      // Para a função open()
#include <unistd.h>     // Para read(), write(), pread(), pwrite(), close()
#include <stdint.h>     // Para uint32_t

// Endereços Base definidos no Qsys
#define RED_LEDS_OFFSET 0xC0A0
#define BUTTONS_OFFSET  0xC080

int main() {
    // 1. Abre o arquivo do Character Device criado pelo seu Driver
    int fd = open("/dev/de2i150_dev", O_RDWR);
    if (fd < 0) {
        perror("Falha ao abrir o dispositivo. O driver foi carregado com insmod?");
        return -1;
    }

    printf("Ponte com o Kernel aberta com sucesso!\n");

    // 2. Teste de ESCRITA: Acender LEDs alternados (Padrão 101010)
    uint32_t leds = 0b101010; 
    
    // A função pwrite escreve a variável 'leds' exatamente no offset do RED_LEDS
    if (pwrite(fd, &leds, sizeof(uint32_t), RED_LEDS_OFFSET) != sizeof(uint32_t)) {
        perror("Erro ao escrever nos LEDs");
    } else {
        printf("Comando enviado para acender os LEDs!\n");
    }

    // 3. Teste de LEITURA: Ler o estado dos Botões
    uint32_t botoes = 0;
    
    // A função pread lê exatamente do offset dos BUTTONS e salva na variável 'botoes'
    if (pread(fd, &botoes, sizeof(uint32_t), BUTTONS_OFFSET) != sizeof(uint32_t)) {
        perror("Erro ao ler os botoes");
    } else {
        // Imprime o valor em hexadecimal
        printf("Estado atual dos botoes: 0x%X\n", botoes);
    }

    // 4. Fecha o arquivo
    close(fd);
    printf("Aplicacao encerrada.\n");
    
    return 0;
}