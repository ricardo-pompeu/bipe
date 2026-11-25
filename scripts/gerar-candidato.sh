#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -eu
[ "${GITHUB_REF:-}" = refs/heads/main ] || { echo 'Candidatos oficiais exigem main.' >&2; exit 1; }
unset BIPE_GPG_KEY BIPE_GPG_HOMEDIR
work=$(mktemp -d)
sh scripts/build-flatpak.sh "$work/build" "$work/repo"
/usr/bin/python3 scripts/verificar-bundle.py Bipe.flatpak
mkdir -p candidate
cp Bipe.flatpak candidate/
python3 - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
from bipe import VERSION
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert commit==os.environ['GITHUB_SHA']
data={'repository':os.environ['GITHUB_REPOSITORY'],'run_id':os.environ['GITHUB_RUN_ID'],'source_commit':commit,'version':VERSION,'bundle_sha256':hashlib.sha256(Path('candidate/Bipe.flatpak').read_bytes()).hexdigest()}
Path('candidate/candidate.json').write_text(json.dumps(data,indent=2)+'\n')
PY
