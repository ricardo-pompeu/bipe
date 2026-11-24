# Validação

## Automatizados

```sh
/usr/bin/python3 -m unittest discover -s tests -v
meson test -C build --print-errorlogs
```

A suíte cobre cadastro e duplicidade, busca por código/nome com acentos, leituras repetidas, quantidades, subtotais, total, dinheiro e troco, rejeição de valores inválidos, persistência ao reabrir SQLite, histórico com preço/nome original, conclusão idempotente, PDF em 58/80 mm, reimpressão, falha simulada no adaptador real de impressão preservando a venda, backup/restauração/retenção, rejeição de backup inválido, rollback de venda incompleta e nomes longos. O teste offline bloqueia a criação de sockets Python e executa venda, backup e PDF; a aplicação não usa rede.

Teste de interface, com dados e cache temporários, sem modificar a loja real:

```sh
/usr/bin/python3 scripts/smoke_ui.py
```

Em ambiente sem display, pode-se iniciar `gtk4-broadwayd :17` e executar:

```sh
GDK_BACKEND=broadway BROADWAY_DISPLAY=:17 GSETTINGS_BACKEND=memory /usr/bin/python3 scripts/smoke_ui.py
```

Broadway é apenas um backend gráfico para teste; o programa instalado usa a sessão GNOME normal. A interface do aplicativo é inteiramente GTK/Libadwaita.

## Impressora física e portal Flatpak (requer equipamento)

1. Instale a térmica no CUPS e confirme uma página de teste do próprio sistema.
2. Instale o pacote Flatpak e abra pelo menu.
3. Em Preferências, escolha 58 mm e selecione a térmica pelo diálogo nativo. Confira escala 100%, margens e bobina no driver.
4. Use Testar impressão. Confira acentos, quebra de nome longo, largura, total e marca de teste, sem criar venda no histórico.
5. Cadastre Arroz 1 kg por R$ 7,50; leia duas vezes, finalize em dinheiro com R$ 20,00. Verifique quantidade 2, total R$ 15,00 e troco R$ 5,00 no papel.
6. Desligue a impressora ou pause a fila. Conclua outra venda; confirme que aparece no histórico, mesmo cancelando/recebendo erro de impressão. Religue e reimprima a mesma venda; o número deve permanecer igual e o histórico não deve crescer.
7. Feche/reabra; confira produtos e vendas persistentes e nova seleção de impressora. Teste Salvar PDF pelo portal fora do sandbox e Visualizar PDF.
8. Repita com 80 mm e uma compra longa. Alguns drivers impõem comprimento máximo: valide corte/paginação na térmica específica antes de uso comercial.
9. Teste com rede desligada, leitor USB real e GNOME em tema claro, escuro e alto contraste; confira navegação com Tab/Enter e leitura assistiva.
10. Exporte backup, cadastre um produto extra, restaure com confirmação e verifique o desaparecimento do produto extra e a existência da cópia anterior. Faça isso em dados de teste.

O envio aceito pelo CUPS não garante saída física: acompanhe a fila do sistema quando houver falta de papel. Testes automatizados de falha usam um backend substituto e não certificam hardware ou portal.

## Resultado nesta máquina — 19/10/2026

- 12 testes de lógica/PDF passaram com o Python do sistema e novamente no SDK GNOME 50 durante a construção do Flatpak.
- Meson configurou, instalou em diretório de estágio e passou sua suíte.
- O pacote `CaixaSimples.flatpak` foi construído e instalado para o usuário.
- `scripts/smoke_ui.py` passou no GTK do sistema e no runtime do Flatpak instalado, usando Broadway com banco/cache temporários. Verificou a construção de todas as telas e diálogos.
- `scripts/acceptance_ui.py` percorre os callbacks reais de cadastro, leitura repetida, recebimento de R$ 20,00 para compra de R$ 15,00, conclusão pelo botão, falha controlada de impressão e nova tentativa sem duplicação. O PDF é real; o envio à impressora é substituído somente neste teste.
- O arquivo desktop passou em `desktop-file-validate`.
- AppStream: aviso conhecido `url-homepage-missing`; não se inventou uma homepage pública para o projeto ainda local.
- Não foram certificados impressão física, interação com o portal de impressão em sessão GNOME, corte da térmica, leitor USB físico e leitor de tela. A chamada nativa de impressão está implementada; os testes de falha são controlados e não substituem essa validação no equipamento real.


## Atualização 0.2.0 — 20/10/2026

A suíte passou com 17 testes, incluindo os cinco novos de produtos vendidos por dia: estado vazio, quantidades/ordenação, separação por data e nomes históricos, agrupamento do mesmo produto após mudança de nome e persistência do resumo após backup/restauração/reabertura. Carrinhos sem conclusão ficam fora do resumo. Não houve alteração no formato do banco.

O teste gráfico adicional pode ser executado com:

```sh
GDK_BACKEND=broadway BROADWAY_DISPLAY=:19 GSETTINGS_BACKEND=memory /usr/bin/python3 scripts/closing_ui.py
```

Ele verifica a nova aba, estado vazio, ícone disponível, atualização ao entrar na aba, calendário, seleção de data anterior e retorno a Hoje. Os testes gráficos usam bancos temporários e instâncias independentes, preservando a loja em uso.

A construção 0.2.0 passou nos 17 testes dentro do SDK GNOME 50. O pacote foi instalado e `scripts/closing_ui.py` também passou usando o código instalado no Flatpak. O fluxo completo de venda foi verificado novamente com dados isolados.

## Catálogo e assinatura — 0.4.3, 23/11/2026

A suíte de 25 testes passou no SDK GNOME 50. O compositor AppStream validou o metainfo e gerou o catálogo e os ícones. A API libflatpak verificou o catálogo extraído do próprio arquivo Bipe.flatpak, incluindo nome, responsável, descrição, três screenshots e ícones PNG de 64 e 128 px. A assinatura GPG de SHA256SUMS foi validada com a chave pública da distribuição e os hashes dos arquivos conferiram. As capturas foram geradas com dados de demonstração em banco temporário e não envolveram impressão.

As imagens ficam no repositório público bipe-media por autorização do mantenedor; os URLs fixam o commit da publicação. A certificação de identidade do autor por terceiros não foi realizada e não é prometida pela assinatura.

## Origem oficial no GitHub Pages — 0.4.4, 23/11/2026

A origem HTTPS do próprio repositório foi adicionada ao Flatpak com verificação GPG ativa. O catálogo foi baixado pelo Flatpak e interpretado pela API AppStream: três capturas foram selecionadas para o tamanho usado na loja. O novo caminho de instalação é Bipe.flatpakref, que usa o catálogo da origem, em vez do fluxo limitado de abertura de um bundle local. A geração do catálogo usa libappstream e librsvg no SDK.

A suíte de 25 testes e a verificação de metadados dentro do pacote passaram. Os commits do aplicativo, o catálogo e o resumo do repositório são assinados. Os scripts de publicação não copiam a chave secreta; apenas os artefatos públicos são enviados à branch gh-pages.

## Estoque opcional e valores no fechamento — 0.5.0

38 testes cobrem estoque desativado por padrão, baixa somente ao concluir a venda, idempotência, aviso no limite escolhido, saldo negativo sem bloquear venda, reposição/desativação, rollback conjunto de venda e estoque, backup/restauração e migração do esquema 1 para o 2. O fechamento soma os preços históricos de cada venda, inclusive quando o produto teve preços diferentes no mesmo dia.

Os testes gráficos stock_ui.py, closing_ui.py e acceptance_ui.py passaram com banco temporário e impressão substituída por um backend de teste. Conferiram o formulário opcional, baixa, aviso, reimpressão sem novo desconto, reposição, calendário e valores. O formulário foi renderizado e revisado com o botão Salvar fixo. As capturas da loja foram atualizadas com dados de demonstração.

Uma migração adicional foi executada em cópia consistente do banco local: produtos, vendas, itens e preferências foram comparados antes e depois. O banco original não foi alterado nessa verificação.

## Simplificação do estoque e venda — 0.6.0

`tests/test_stock.py` verifica campo vazio, zero, validação de inteiros e limite global persistido, independente dos antigos limites por produto. `scripts/stock_ui.py` percorre cadastro, venda, reposição, preferências e desativação pelo campo vazio. `scripts/layout_ui.py` confere leitor, total e ações dentro de janelas de 850×490 e 640×420, com alerta e carrinho rolável, e gera capturas em /tmp. Os testes de interface usam dados temporários e não imprimem.
