#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Execute após empacotar-site.sh. Mantém os objetos já publicados do repositório.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
site="$root/dist/github-pages"
[ -s "$site/repo/summary.sig" ] || { echo 'Gere o catálogo assinado primeiro com empacotar-site.sh.' >&2; exit 1; }
python3 "$root/scripts/verificar-publicacao.py" "$site" "$root/security/Bipe-signing-key.asc"
stage=$(mktemp -d /tmp/bipe-pages-publish.XXXXXX)
git clone --branch gh-pages --single-branch https://github.com/ricardo-pompeu/bipe.git "$stage"
if command -v gh >/dev/null 2>&1; then
    git -C "$stage" config credential.https://github.com.helper '!gh auth git-credential'
fi
cp -a "$site/." "$stage/"
git -C "$stage" add .
if git -C "$stage" diff --cached --quiet; then
    echo 'Os arquivos já estão publicados.'
else
    git -C "$stage" commit -m 'Atualiza a distribuição assinada do Bipe'
    git -C "$stage" push origin gh-pages
fi

commit=$(git -C "$stage" rev-parse HEAD)
gh workflow run publicar.yml --repo ricardo-pompeu/bipe --ref main -f "distribution_commit=$commit"
printf '%s\n' 'Candidato de catálogo enviado. Aprove o deployment github-pages no GitHub para chegar à loja.'
