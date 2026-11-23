<div align="center">

<img src="data/bipe-icon-preview.png" width="128" height="128" alt="Ícone do Bipe">

# Bipe

Um caixa simples para sua loja. Cadastre produtos, venda e imprima comprovantes.

### [⬇ Baixar Bipe para Linux](https://github.com/ricardo-pompeu/bipe/releases/latest/download/Bipe.flatpak)

Linux de 64 bits (Intel/AMD) · Funciona offline após a instalação

</div>

## Instalar e começar

1. Clique em **Baixar Bipe para Linux**.
2. Abra o arquivo **Bipe.flatpak** e confirme **Instalar** ou **Atualizar**.
3. Abra **Bipe** no menu de aplicativos.

O Linux precisa ter suporte a Flatpak. Se o arquivo não abrir, veja o [passo a passo de instalação](INSTALACAO.md#instalação-manual-sem-preparação-da-impressora).

**Já tem o Bipe?** Baixe o arquivo novamente para atualizar. Seus produtos, vendas e preferências são preservados. Feche o aplicativo antes de atualizar.

> O repositório é privado. Para baixar, entre no GitHub com uma conta que tenha acesso.

## Usar com a impressora POS-80

[**⬇ Baixar Bipe com configuração da POS-80**](https://github.com/ricardo-pompeu/bipe/releases/latest/download/Bipe-POS80-linux-x86_64.tar.gz)

Extraia o kit, conecte a impressora por USB e abra o terminal na pasta extraída. Execute:

```sh
sh instalar-bipe.sh
```

O instalador prepara a impressora e instala o Bipe. Se o Bipe já estiver instalado, ele atualiza o aplicativo. Para configurar somente a impressora, use `sh instalar-bipe.sh --so-impressora`. [Ver as instruções completas](INSTALACAO.md#instalação-automática-com-a-pos-80-usb).

## No dia a dia

- **Vender:** passe o produto no leitor ou digite o código. Escolha o pagamento e finalize.
- **Produtos:** cadastre ou altere o nome e o preço.
- **Fechamento:** veja as quantidades vendidas e os produtos mais vendidos do dia.

O menu também oferece vendas recentes, reimpressão e backup.

O Bipe emite **comprovantes não fiscais**.

---

[Instalação e migração de dados](INSTALACAO.md) · [Guia técnico](docs/GUIA-TECNICO.md) · [Testes](TESTES.md) · [Autenticidade do pacote](docs/GUIA-TECNICO.md#informações-da-gnome-software-e-assinatura) · [Licença GPL](LICENSE)
