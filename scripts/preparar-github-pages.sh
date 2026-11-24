#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Publica apenas o repositório Flatpak e arquivos públicos, nunca o chaveiro privado.
set -eu
source_repo=${1:?Informe o repositório Flatpak gerado pelo empacotamento}
out=${2:?Informe a pasta de saída para o GitHub Pages}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
keyhome=${BIPE_GPG_HOMEDIR:-"$HOME/.local/share/bipe-release-signing"}
key=${BIPE_GPG_KEY:-6C5D151C77B132C6F4D18FC05F6B9FFE309ADBD1}
base='https://ricardo-pompeu.github.io/bipe'
mkdir -p "$out/repo"
cp -a "$source_repo/." "$out/repo/"
flatpak build-update-repo --title='Bipe — Ricardo Pompeu' \
    --comment='Distribuição oficial do Bipe' --homepage=https://github.com/ricardo-pompeu/bipe \
    --default-branch=master --gpg-sign="$key" --gpg-homedir="$keyhome" "$out/repo"
gpg --homedir "$keyhome" --batch --armor --export "$key" > "$out/Bipe-signing-key.asc"
cp "$root/data/bipe-icon-preview.png" "$out/icon.png"
cp "$root/scripts/conectar-repositorio-bipe.sh" "$out/"
cp "$root/LICENSE" "$out/"
mkdir -p "$out/screenshots"
cp "$root"/data/screenshots/*.png "$out/screenshots/"
cat > "$out/index.html" <<'HTML'
<!doctype html>
<html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Bipe — instalação oficial</title>
<body><main><h1>Bipe</h1><p>Um caixa simples para sua loja.</p>
<p><a href="Bipe.flatpakref">Instalar Bipe na loja do Linux</a></p>
<p>Linux x86_64 com Flatpak. Origem de distribuição: Ricardo Pompeu.</p>
<p><a href="https://github.com/ricardo-pompeu/bipe">Código-fonte e instruções</a> · <a href="Bipe-signing-key.asc">Chave pública</a></p>
<p>Pacotes assinados. Isso não representa certificação do GNOME ou do Flathub.</p></main></body></html>
HTML
cat > "$out/.gitignore" <<'IGNORE'
repo/.lock
repo/tmp/
repo/state/
IGNORE
touch "$out/.nojekyll"
pubkey=$(gpg --homedir "$keyhome" --batch --export "$key" | base64 -w 0)
cat > "$out/Bipe.flatpakref" <<REF
[Flatpak Ref]
Name=io.github.ricardo_pompeu.Bipe
Branch=master
Title=Bipe
Comment=Um caixa simples para pequenos comércios
Url=$base/repo/
SuggestRemoteName=bipe
RuntimeRepo=https://dl.flathub.org/repo/flathub.flatpakrepo
IsRuntime=false
GPGKey=$pubkey
REF
cat > "$out/Bipe.flatpakrepo" <<REPO
[Flatpak Repo]
Title=Bipe — Ricardo Pompeu
Url=$base/repo/
Homepage=https://github.com/ricardo-pompeu/bipe
Comment=Distribuição oficial do Bipe
DefaultBranch=master
GPGKey=$pubkey
REPO
printf '%s\n' "Arquivos públicos preparados em $out"
