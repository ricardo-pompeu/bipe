#!/usr/bin/python3
"""Assinatura local de candidato do CI. Não executa código contido no candidato."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPOSITORY = 'ricardo-pompeu/bipe'
def output(*args):
    return subprocess.check_output(args, text=True).strip()

def main():
    if len(sys.argv) != 3 or not sys.argv[1].isdigit() or not re.fullmatch('[0-9a-f]{64}', sys.argv[2]):
        raise SystemExit('Uso: python3 scripts/promover-candidato.py RUN_ID SHA256_APROVADO')
    run, expected = sys.argv[1:]
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    assert not output('git', 'status', '--porcelain'), 'Use uma cópia Git limpa do commit candidato.'
    head = output('git', 'rev-parse', 'HEAD')
    metadata = json.loads(output('gh', 'api', f'repos/{REPOSITORY}/actions/runs/{run}'))
    assert metadata['conclusion'] == 'success' and metadata['status'] == 'completed'
    assert metadata['head_branch'] == 'main' and metadata['head_sha'] == head
    assert metadata['path'] == '.github/workflows/candidato.yml'
    assert metadata['event'] == 'workflow_dispatch'
    with tempfile.TemporaryDirectory(prefix='bipe-review-') as temporary:
        folder = Path(temporary)
        subprocess.run(['gh','run','download',run,'--repo',REPOSITORY,'--name','candidato-bipe','--dir',temporary],check=True)
        data = json.loads((folder/'candidate.json').read_text())
        bundle = folder/'Bipe.flatpak'
        assert not bundle.is_symlink() and bundle.is_file()
        assert hashlib.sha256(bundle.read_bytes()).hexdigest() == expected == data['bundle_sha256']
        assert data['source_commit'] == head and str(data['run_id']) == run and data['repository'] == REPOSITORY
        from bipe import VERSION
        assert data['version'] == VERSION
        data['reviewer'] = output('gh','api','user','--jq','.login')
        data['decision'] = 'approved-for-signing'
        (folder/'review.json').write_text(json.dumps(data,indent=2)+'\n')
        env = dict(os.environ, BIPE_CANDIDATE_BUNDLE=str(bundle), BIPE_REVIEW_FILE=str(folder/'review.json'))
        subprocess.run(['sh','scripts/empacotar-site.sh'],env=env,check=True)
    print('Assinado. Revise dist/github-pages/review.json e execute sh scripts/publicar-github-pages.sh. A loja só muda após aprovação do ambiente github-pages.')

if __name__ == '__main__':
    main()
