#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Vincula o Bipe existente ao repositório oficial sem apagar dados.
set -eu
[ "$(id -u)" != 0 ] || { echo 'Execute sem sudo, com seu usuário.' >&2; exit 1; }
ref='io.github.ricardo_pompeu.Bipe/x86_64/master'
scope=user
user=false
if flatpak info --user "$ref" >/dev/null 2>&1; then user=true; fi
if flatpak info --system "$ref" >/dev/null 2>&1; then
    [ "$user" = false ] || { echo 'Há duas instalações do Bipe. Escolha uma antes de continuar.' >&2; exit 1; }
    scope=system
fi
url='https://ricardo-pompeu.github.io/bipe/Bipe.flatpakrepo'
flatpak remote-add "--$scope" --if-not-exists bipe "$url"
remote_url=$(flatpak remotes "--$scope" --columns=name,url | awk '$1=="bipe" {print $2}')
[ "$remote_url" = 'https://ricardo-pompeu.github.io/bipe/repo/' ] || { echo 'A origem bipe existente usa outro endereço; ela foi preservada.' >&2; exit 1; }
flatpak remote-modify "--$scope" --gpg-verify bipe
actual=$(flatpak remote-info "--$scope" --show-ref bipe "$ref")
[ "$actual" = "app/$ref" ] || { echo 'O repositório não apresentou o identificador esperado.' >&2; exit 1; }
if flatpak info "--$scope" "$ref" >/dev/null 2>&1; then
    if [ "$(flatpak info "--$scope" --show-origin "$ref")" = bipe ]; then
        flatpak update "--$scope" --noninteractive "$ref"
    else
        flatpak install "--$scope" --or-update --reinstall --noninteractive bipe "$ref"
    fi
else
    flatpak install "--$scope" --or-update --noninteractive bipe "$ref"
fi
echo 'Bipe conectado à distribuição oficial. As próximas atualizações poderão aparecer na loja do Linux.'
