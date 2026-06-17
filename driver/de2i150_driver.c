#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/fs.h>       // Para operações de arquivo (read, write)
#include <linux/cdev.h>     // Para o Character Device
#include <linux/uaccess.h>  // Para copy_to_user e copy_from_user

#define ALTERA_VENDOR_ID 0x1172
#define ALTERA_DEVICE_ID 0x0004

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Equipe IHS");
MODULE_DESCRIPTION("Driver PCIe e Character para DE2i-150 - Projeto IHS");

// Variáveis globais do driver
void __iomem *de2i150_mem = NULL;
static dev_t dev_num;           // Número do dispositivo (Major/Minor)
static struct cdev my_cdev;     // Estrutura do Character Device
static struct class *my_class;  // Classe do dispositivo (para aparecer em /dev/)

/* ================================================================
 * OPERAÇÕES DE ARQUIVO (A Ponte com o User Space)
 * ================================================================ */

static int de2i150_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "DE2i-150 Driver: Arquivo /dev/ aberto!\n");
    return 0;
}

static int de2i150_release(struct inode *inode, struct file *file) {
    printk(KERN_INFO "DE2i-150 Driver: Arquivo /dev/ fechado.\n");
    return 0;
}

// Quando a aplicação der um read(), lemos do FPGA e mandamos para o User Space
static ssize_t de2i150_read(struct file *file, char __user *user_buf, size_t size, loff_t *offset) {
    uint32_t valor_lido;
    
    // Lê 32 bits do endereço físico base + offset
    valor_lido = ioread32(de2i150_mem + *offset);
    
    // Copia o valor lido do Kernel para a variável lá na aplicação do usuário
    if (copy_to_user(user_buf, &valor_lido, sizeof(uint32_t))) {
        return -EFAULT;
    }
    
    return sizeof(uint32_t); // Retorna quantos bytes foram lidos
}

// Quando a aplicação der um write(), pegamos o valor do User Space e jogamos no FPGA
static ssize_t de2i150_write(struct file *file, const char __user *user_buf, size_t size, loff_t *offset) {
    uint32_t valor_escrito;
    
    // Pega o valor enviado pela aplicação do usuário para o Kernel
    if (copy_from_user(&valor_escrito, user_buf, sizeof(uint32_t))) {
        return -EFAULT;
    }

    // Escreve os 32 bits no endereço físico base + offset
    iowrite32(valor_escrito, de2i150_mem + *offset);
    
    return sizeof(uint32_t); // Retorna quantos bytes foram escritos
}

// Associa as nossas funções aos comandos padrão do Linux
static struct file_operations fops = {
    .owner   = THIS_MODULE,
    .open    = de2i150_open,
    .release = de2i150_release,
    .read    = de2i150_read,
    .write   = de2i150_write,
};


/* ================================================================
 * FUNÇÕES PCI (Probe e Remove)
 * ================================================================ */

static int de2i150_probe(struct pci_dev *pdev, const struct pci_device_id *id) {
    int err;
    resource_size_t mmio_start, mmio_len;

    printk(KERN_INFO "DE2i-150 Driver: Iniciando Probe...\n");

    // 1. Habilita PCI e mapeia memória
    err = pci_enable_device(pdev);
    if (err) return err;

    err = pci_request_regions(pdev, "de2i150_driver");
    if (err) goto err_regions;

    mmio_start = pci_resource_start(pdev, 0); 
    mmio_len = pci_resource_len(pdev, 0);

    de2i150_mem = ioremap(mmio_start, mmio_len);
    if (!de2i150_mem) {
        err = -EIO;
        goto err_ioremap;
    }

    // 2. Configura o Character Device (Cria o /dev/de2i150_dev)
    if (alloc_chrdev_region(&dev_num, 0, 1, "de2i150_dev") < 0) {
        err = -EFAULT;
        goto err_chrdev;
    }

    cdev_init(&my_cdev, &fops);
    if (cdev_add(&my_cdev, dev_num, 1) < 0) {
        err = -EFAULT;
        goto err_cdev_add;
    }

    my_class = class_create(THIS_MODULE, "de2i150_class");
    device_create(my_class, NULL, dev_num, NULL, "de2i150_dev"); // Gera o arquivo no /dev/

    printk(KERN_INFO "DE2i-150 Driver: Pronto! Arquivo /dev/de2i150_dev criado.\n");
    return 0;

// Tratamento de erros (rollback)
err_cdev_add:
    unregister_chrdev_region(dev_num, 1);
err_chrdev:
    iounmap(de2i150_mem);
err_ioremap:
    pci_release_regions(pdev);
err_regions:
    pci_disable_device(pdev);
    return err;
}

static void de2i150_remove(struct pci_dev *pdev) {
    // Destrói o Character Device
    device_destroy(my_class, dev_num);
    class_destroy(my_class);
    cdev_del(&my_cdev);
    unregister_chrdev_region(dev_num, 1);

    // Destrói o mapeamento PCI
    if (de2i150_mem) iounmap(de2i150_mem);
    pci_release_regions(pdev);
    pci_disable_device(pdev);
    
    printk(KERN_INFO "DE2i-150 Driver: Removido com seguranca.\n");
}

static struct pci_device_id pci_ids[] = {
    { PCI_DEVICE(ALTERA_VENDOR_ID, ALTERA_DEVICE_ID), },
    { 0, }
};
MODULE_DEVICE_TABLE(pci, pci_ids);

static struct pci_driver de2i150_pci_driver = {
    .name = "de2i150_driver",
    .id_table = pci_ids,
    .probe = de2i150_probe,
    .remove = de2i150_remove,
};

static int __init de2i150_init(void) {
    return pci_register_driver(&de2i150_pci_driver);
}

static void __exit de2i150_exit(void) {
    pci_unregister_driver(&de2i150_pci_driver);
}

module_init(de2i150_init);
module_exit(de2i150_exit);