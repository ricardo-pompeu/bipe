#!/bin/sh
# Constrói o mesmo módulo do manifesto usando o SDK instalado, sem downloads.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=${1:-/tmp/bipe-flatpak-build}
repo=${2:-/tmp/bipe-flatpak-repo}
# Identidade permanente: não incluir a versão no ID ou no canal.
python3 - "$root" <<'CHECK'
import ast, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / 'io.github.ricardo_pompeu.Bipe.json').read_text())
module = ast.parse((root / 'bipe/__init__.py').read_text())
app_id = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'APP_ID' for t in n.targets))
assert app_id == manifest['app-id'] == 'io.github.ricardo_pompeu.Bipe', 'O identificador deve permanecer igual entre versões.'
CHECK
flatpak build-init "$work" io.github.ricardo_pompeu.Bipe org.gnome.Sdk org.gnome.Platform 50
flatpak build --filesystem="$root":ro "$work" sh -ec 'meson setup /tmp/caixa-meson "$1" --prefix=/app; meson test -C /tmp/caixa-meson --print-errorlogs; meson install -C /tmp/caixa-meson' sh "$root"
flatpak build-finish --socket=cups --share=ipc --socket=wayland --socket=fallback-x11 --device=dri --command=bipe "$work"
flatpak build-export "$repo" "$work" master
flatpak build-bundle --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo "$repo" "$root/Bipe.flatpak" io.github.ricardo_pompeu.Bipe master
