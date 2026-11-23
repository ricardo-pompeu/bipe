#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Constrói e prepara os arquivos com nomes fixos para o botão Baixar do site.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BIPE_GPG_HOMEDIR=${BIPE_GPG_HOMEDIR:-"$HOME/.local/share/bipe-release-signing"}
BIPE_GPG_KEY=${BIPE_GPG_KEY:-6C5D151C77B132C6F4D18FC05F6B9FFE309ADBD1}
export BIPE_GPG_HOMEDIR BIPE_GPG_KEY
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --list-secret-keys "$BIPE_GPG_KEY" >/dev/null
work=$(mktemp -d /tmp/bipe-release.XXXXXX)
sh "$root/scripts/build-flatpak.sh" "$work/build" "$work/repo"
/usr/bin/python3 "$root/scripts/verificar-bundle.py" "$root/Bipe.flatpak"
out="$root/dist"
mkdir -p "$out" "$work/Bipe-POS80"
cp "$root/Bipe.flatpak" "$out/Bipe.flatpak"
cp "$root/Bipe.flatpak" "$work/Bipe-POS80/"
cp "$root"/scripts/instalar-bipe.sh "$root"/scripts/instalar-caixa-simples.sh \
   "$root"/scripts/atualizar-bipe.sh "$root"/scripts/migrar-bipe.py \
   "$root/INSTALACAO.md" "$root/LICENSE" "$work/Bipe-POS80/"
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --armor --export "$BIPE_GPG_KEY" > "$work/Bipe-POS80/Bipe-signing-key.asc"
(cd "$work/Bipe-POS80" && sha256sum Bipe.flatpak > SHA256SUMS)
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --yes --local-user "$BIPE_GPG_KEY" --armor --detach-sign "$work/Bipe-POS80/SHA256SUMS"
tar -czf "$out/Bipe-POS80-linux-x86_64.tar.gz" -C "$work" Bipe-POS80
cp "$work/Bipe-POS80/Bipe-signing-key.asc" "$out/"
(cd "$out" && sha256sum Bipe.flatpak Bipe-POS80-linux-x86_64.tar.gz > SHA256SUMS)
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --yes --local-user "$BIPE_GPG_KEY" --armor --detach-sign "$out/SHA256SUMS"
printf '%s\n' 'Arquivos prontos em dist/. Publique-os no site substituindo os anteriores, sem mudar o endereço do botão Baixar.'
