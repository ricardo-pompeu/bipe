# Distribuição do Bipe

O Bipe mantém o ID, o canal e o endereço atuais. A infraestrutura pode ser migrada depois sem criar outro aplicativo, desde que preserve a identidade e a confiança na assinatura.

## Fluxo

1. Alterações entram por pull request. O check **Testes e política** executa testes e verifica as permissões Flatpak previstas. Não há chave de assinatura nem token de escrita nos builds.
2. Um curador inicia **Construir candidato** em Actions, em `main`. A máquina descartável constrói e testa o Flatpak; o artefato `candidato-bipe` contém o pacote e `candidate.json` com commit, execução e SHA-256.
3. O curador examina o código e o candidato, inclusive funcionamento, dependências e permissões. Um build bem-sucedido não substitui essa revisão. Instale candidatos apenas em ambiente de teste; eles não são o canal estável.
4. Em uma cópia Git limpa do mesmo commit, no computador autorizado a assinar, execute:

   ```sh
   python3 scripts/promover-candidato.py RUN_ID SHA256_APROVADO
   ```

   Copie os dois valores do relatório de Actions depois de revisar. O comando consulta a execução oficial, confere commit e hash e importa o candidato, sem reconstruir nem executar o aplicativo. A chave GPG permanece local. A assinatura pode alterar o envelope do bundle; o conteúdo OSTree do aplicativo é preservado.
5. Execute `sh scripts/publicar-github-pages.sh`. Isso envia o catálogo assinado a `gh-pages` e solicita o workflow **Publicar catálogo aprovado**. Um push nessa branch, sozinho, não atualiza mais a loja.
6. O workflow verifica a assinatura fixada e os hashes de todos os arquivos. Em seguida, aguarda a aprovação humana do ambiente **github-pages** em Actions. Confira o commit de distribuição e `review.json` antes de aprovar. Somente então o artefato verificado é servido na origem oficial.

Não publique downloads da versão final no GitHub Releases antes de concluir a aprovação. A entrega à loja e os downloads manuais são canais diferentes.

## Papéis e limites

Ricardo Pompeu é o curador e administrador inicial. A aprovação do ambiente é obrigatória e o bypass administrativo de deployments fica desativado. Como há apenas um curador, ele pode aprovar uma execução que iniciou. Isso é uma aprovação explícita, **não uma revisão independente por duas pessoas**. Antes de aceitar terceiros, cadastre outro curador, exija revisão de PR por outra pessoa e ative o bloqueio de autoaprovação do deployment.

O administrador do repositório pode alterar as próprias proteções. Nenhuma configuração torna o proprietário incapaz de modificar sua infraestrutura. Use conta protegida por autenticação forte, revisão dos acessos e, ao crescer, organização e papéis separados.

`main` exige PR, testes, conversas resolvidas e bloqueia force push/exclusão. A fase com curador único não exige aprovação de outro usuário no PR. `CODEOWNERS` indica os responsáveis pelos scripts, workflows e chave pública. Alterá-los é uma mudança da infraestrutura de confiança e exige atenção especial.

Não há chave privada ou segredo de assinatura no GitHub Actions. A chave pública em `security/` e o fingerprint no verificador fixam a identidade atual. Não troque essa confiança em uma atualização comum sem planejar uma rotação. Builds continuam dependendo do SDK e das ferramentas do runner; não alegamos builds integralmente reproduzíveis, atestação SLSA ou detecção garantida de malware.

A checagem de permissões é uma política explícita, não um antivírus. Mudanças maliciosas podem usar acessos existentes. A revisão de cada versão é necessária, inclusive sem mudança de permissões.

## Incidentes

Cancele publicações pendentes e suspenda novas aprovações. Preserve logs, hashes e o pacote suspeito. Revise acessos e a possível exposição da chave; emita uma atualização corrigida e comunique os usuários. Remover um pacote do catálogo não o desinstala das máquinas. Voltar a servir um commit antigo não garante downgrade automático pelo Flatpak.

## Migração futura

Separe o catálogo, os workflows e o publicador em repositórios administrados pela futura organização. Desenvolvedores de aplicativos devem ter permissão de submissão, sem escrita em produção nem acesso às chaves. Mantenha aprovação por versão, ambiente de build descartável e publicador sem execução de scripts dos candidatos.
