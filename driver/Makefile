# Nome do módulo que será gerado
obj-m := de2i150_driver.o

# Caminho para os cabeçalhos do Kernel do Linux
# (O comando 'uname -r' pega a versão exata do kernel que está rodando na placa)
KDIR := /lib/modules/$(shell uname -r)/build

# Diretório atual onde os arquivos .c estão
PWD := $(shell pwd)

# Comando padrão de compilação
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Comando para limpar os arquivos de compilação
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean