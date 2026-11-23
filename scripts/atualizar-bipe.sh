#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Mesmo pacote para primeira instalação e atualizações, sem mexer no CUPS.
set -eu
[ "$(id -u)" != 0 ] || { echo 'Execute como seu usuário, sem sudo.' >&2; exit 1; }
command -v flatpak >/dev/null 2>&1 || { echo 'Instale o Flatpak pelo gerenciador de aplicativos do Linux.' >&2; exit 1; }
folder=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bundle="$folder/Bipe.flatpak"
[ -r "$bundle" ] || { echo 'Coloque Bipe.flatpak na mesma pasta deste script.' >&2; exit 1; }
if [ -f "$folder/SHA256SUMS" ]; then
    (cd "$folder" && sha256sum -c SHA256SUMS)
fi
app='io.github.ricardo_pompeu.Bipe'
ref="$app/x86_64/master"
scope=user
installed=false
if flatpak info --user "$ref" >/dev/null 2>&1; then installed=true; fi
if flatpak info --system "$ref" >/dev/null 2>&1; then
    if [ "$installed" = true ]; then
        echo 'Há instalações do Bipe para seu usuário e para o sistema. Escolha qual manter antes de atualizar.' >&2
        exit 1
    fi
    scope=system
    installed=true
fi
if [ "$installed" = true ]; then
    echo 'Atualizando o Bipe existente; produtos, vendas e preferências serão preservados.'
else
    echo 'Instalando o Bipe para seu usuário.'
fi
runtime='org.gnome.Platform/x86_64/50'
if ! flatpak info "--$scope" "$runtime" >/dev/null 2>&1; then
    flatpak remote-add "--$scope" --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak install "--$scope" --noninteractive flathub "$runtime"
fi
if [ "$installed" = true ]; then
    flatpak install "--$scope" --bundle --or-update --noninteractive --reinstall "$bundle"
else
    flatpak install "--$scope" --bundle --or-update --noninteractive "$bundle"
fi
echo 'Pronto. Feche e abra o Bipe para usar a versão instalada.'
