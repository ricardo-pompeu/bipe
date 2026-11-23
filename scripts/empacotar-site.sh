#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Constrói e prepara os arquivos com nomes fixos para o botão Baixar do site.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d /tmp/bipe-release.XXXXXX)
sh "$root/scripts/build-flatpak.sh" "$work/build" "$work/repo"
out="$root/dist"
mkdir -p "$out" "$work/Bipe-POS80"
cp "$root/Bipe.flatpak" "$out/Bipe.flatpak"
cp "$root/Bipe.flatpak" "$work/Bipe-POS80/"
cp "$root"/scripts/instalar-bipe.sh "$root"/scripts/instalar-caixa-simples.sh \
   "$root"/scripts/atualizar-bipe.sh "$root"/scripts/migrar-bipe.py \
   "$root/INSTALACAO.md" "$root/LICENSE" "$work/Bipe-POS80/"
(cd "$work/Bipe-POS80" && sha256sum Bipe.flatpak > SHA256SUMS)
tar -czf "$out/Bipe-POS80-linux-x86_64.tar.gz" -C "$work" Bipe-POS80
(cd "$out" && sha256sum Bipe.flatpak Bipe-POS80-linux-x86_64.tar.gz > SHA256SUMS)
printf '%s\n' 'Arquivos prontos em dist/. Publique-os no site substituindo os anteriores, sem mudar o endereço do botão Baixar.'
