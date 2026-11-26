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
# O caminho oficial nunca reconstrói depois da revisão.
: "${BIPE_CANDIDATE_BUNDLE:?Use scripts/promover-candidato.py RUN_ID SHA256_APROVADO}"
: "${BIPE_REVIEW_FILE:?Falta o registro de revisão do candidato}"
/usr/bin/python3 - "$work/repo" <<'INIT'
import sys,gi
gi.require_version('OSTree','1.0')
from gi.repository import OSTree,Gio
repo=OSTree.Repo.new(Gio.File.new_for_path(sys.argv[1]))
repo.create(OSTree.RepoMode.ARCHIVE,None)
INIT
flatpak build-import-bundle --gpg-sign="$BIPE_GPG_KEY" --gpg-homedir="$BIPE_GPG_HOMEDIR" "$work/repo" "$BIPE_CANDIDATE_BUNDLE"
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --export "$BIPE_GPG_KEY" > "$work/public-key.gpg"
flatpak build-bundle --repo-url=https://ricardo-pompeu.github.io/bipe/repo/ --gpg-keys="$work/public-key.gpg" --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo "$work/repo" "$root/Bipe.flatpak" io.github.ricardo_pompeu.Bipe master
/usr/bin/python3 - "$BIPE_CANDIDATE_BUNDLE" "$root/Bipe.flatpak" <<'COMMIT'
import sys,gi
gi.require_version('Flatpak','1.0')
from gi.repository import Flatpak,Gio
before,after=[Flatpak.BundleRef.new(Gio.File.new_for_path(path)) for path in sys.argv[1:]]
assert before.get_commit()==after.get_commit(), 'O conteúdo mudou depois da revisão.'
COMMIT
/usr/bin/python3 "$root/scripts/verificar-bundle.py" "$root/Bipe.flatpak"
out="$root/dist"
mkdir -p "$out" "$work/Bipe-POS80"
cp "$root/Bipe.flatpak" "$out/Bipe.flatpak"
cp "$root/Bipe.flatpak" "$work/Bipe-POS80/"
cp "$root"/scripts/instalar-bipe.sh "$root"/scripts/instalar-caixa-simples.sh \
   "$root"/scripts/atualizar-bipe.sh "$root"/scripts/conectar-repositorio-bipe.sh "$root"/scripts/migrar-bipe.py \
   "$root/INSTALACAO.md" "$root/LICENSE" "$work/Bipe-POS80/"
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --armor --export "$BIPE_GPG_KEY" > "$work/Bipe-POS80/Bipe-signing-key.asc"
(cd "$work/Bipe-POS80" && sha256sum Bipe.flatpak > SHA256SUMS)
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --yes --local-user "$BIPE_GPG_KEY" --armor --detach-sign "$work/Bipe-POS80/SHA256SUMS"
tar -czf "$out/Bipe-POS80-linux-x86_64.tar.gz" -C "$work" Bipe-POS80
cp "$work/Bipe-POS80/Bipe-signing-key.asc" "$out/"
# Preserva todos os objetos já servidos: usuários podem estar baixando versões anteriores.
git clone --depth=1 --branch gh-pages --single-branch https://github.com/ricardo-pompeu/bipe.git "$work/previous"
python3 - "$work/previous" "$out/github-pages" <<'COPY'
import shutil,sys
from pathlib import Path
source,target=map(Path,sys.argv[1:])
target.mkdir(parents=True,exist_ok=True)
for path in source.iterdir():
    if path.name=='.git': continue
    if path.is_dir(): shutil.copytree(path,target/path.name,dirs_exist_ok=True)
    else: shutil.copy2(path,target/path.name)
COPY
sh "$root/scripts/preparar-github-pages.sh" "$work/repo" "$out/github-pages"
# build-update-repo pode remover caches de summaries. Preserve também os antigos
# antes de assinar, pois o commit público continua a servi-los a downloads em andamento.
python3 - "$work/previous" "$out/github-pages" <<'PRESERVE'
import shutil,sys
from pathlib import Path
source,target=map(Path,sys.argv[1:])
for path in source.rglob('*'):
    relative=path.relative_to(source)
    if '.git' in relative.parts: continue
    destination=target/relative
    if path.is_file() and not destination.exists():
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,destination)
PRESERVE
cp "$BIPE_REVIEW_FILE" "$out/github-pages/review.json"
python3 - "$out/github-pages" <<'HASH'
import hashlib,sys,shutil
from pathlib import Path
root=Path(sys.argv[1])
# Arquivos internos mutáveis do OSTree não são conteúdo distribuído.
(root/'repo/.lock').unlink(missing_ok=True)
for folder in ('repo/tmp','repo/state'):
    if (root/folder).exists(): shutil.rmtree(root/folder)
# Descarta comprovantes anteriores antes de gerar o novo manifesto completo.
for name in ('PUBLICATION.sha256','PUBLICATION.sha256.asc'):
    (root/name).unlink(missing_ok=True)
entries=[]
for path in sorted(root.rglob('*')):
    assert not path.is_symlink()
    if path.is_file():
        entries.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+str(path.relative_to(root)))
(root/'PUBLICATION.sha256').write_text('\n'.join(entries)+'\n')
HASH
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --yes --local-user "$BIPE_GPG_KEY" --armor --detach-sign "$out/github-pages/PUBLICATION.sha256"
python3 "$root/scripts/verificar-publicacao.py" "$out/github-pages" "$root/security/Bipe-signing-key.asc"
cp "$out/github-pages/Bipe.flatpakref" "$out/github-pages/Bipe.flatpakrepo" "$out/"
(cd "$out" && sha256sum Bipe.flatpak Bipe-POS80-linux-x86_64.tar.gz Bipe.flatpakref Bipe.flatpakrepo > SHA256SUMS)
gpg --homedir "$BIPE_GPG_HOMEDIR" --batch --yes --local-user "$BIPE_GPG_KEY" --armor --detach-sign "$out/SHA256SUMS"
printf '%s\n' 'Arquivos prontos em dist/. Publique-os no site substituindo os anteriores, sem mudar o endereço do botão Baixar.'
