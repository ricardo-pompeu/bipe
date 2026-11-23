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
# O compositor de ícones usa um sandbox auxiliar via serviço Flatpak.
# Esta permissão pertence somente à construção, não ao aplicativo.
flatpak build --talk-name=org.freedesktop.Flatpak --filesystem="$root":ro "$work" sh -ec 'meson setup /tmp/caixa-meson "$1" --prefix=/app; meson test -C /tmp/caixa-meson --print-errorlogs; meson install -C /tmp/caixa-meson; appstreamcli validate --no-net /app/share/metainfo/io.github.ricardo_pompeu.Bipe.metainfo.xml; appstreamcli compose --no-net --prefix=/ --origin=io.github.ricardo_pompeu.Bipe --result-root=/app --data-dir=/app/share/app-info/xmls --icons-dir=/app/share/app-info/icons/flatpak --components=io.github.ricardo_pompeu.Bipe /app; test -s /app/share/app-info/xmls/io.github.ricardo_pompeu.Bipe.xml.gz' sh "$root"
flatpak build-finish --socket=cups --share=ipc --socket=wayland --socket=fallback-x11 --device=dri --command=bipe "$work"
if [ -n "${BIPE_GPG_KEY:-}" ]; then
    : "${BIPE_GPG_HOMEDIR:?Defina a pasta privada da chave de assinatura}"
    flatpak build-export --gpg-sign="$BIPE_GPG_KEY" --gpg-homedir="$BIPE_GPG_HOMEDIR" "$repo" "$work" master
    public_key="$work/Bipe-signing-key.gpg"
    gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --export "$BIPE_GPG_KEY" > "$public_key"
    flatpak build-bundle --gpg-keys="$public_key" --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo "$repo" "$root/Bipe.flatpak" io.github.ricardo_pompeu.Bipe master
else
    flatpak build-export "$repo" "$work" master
    flatpak build-bundle --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo "$repo" "$root/Bipe.flatpak" io.github.ricardo_pompeu.Bipe master
fi
