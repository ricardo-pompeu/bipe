#!/usr/bin/python3
"""Valida a assinatura fixa e todos os bytes enviados ao Pages, sem executar o site."""
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FINGERPRINT = '6C5D151C77B132C6F4D18FC05F6B9FFE309ADBD1'

def verify(site, key):
    site, key = Path(site).resolve(), Path(key).resolve()
    with tempfile.TemporaryDirectory() as home:
        command = ['gpg', '--homedir', home, '--batch']
        subprocess.run(command + ['--import', str(key)], check=True, capture_output=True)
        result = subprocess.run(command + ['--status-fd', '1', '--verify', str(site/'PUBLICATION.sha256.asc'), str(site/'PUBLICATION.sha256')], check=True, capture_output=True, text=True)
        assert any(line.startswith('[GNUPG:] VALIDSIG ') and line.split()[2] == FINGERPRINT for line in result.stdout.splitlines()), 'Chave inesperada.'
    expected = {}
    for line in (site/'PUBLICATION.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert re.fullmatch('[0-9a-f]{64}', digest)
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and '.git' not in path.parts
        assert name not in expected
        expected[name] = digest
    actual = {}
    for path in site.rglob('*'):
        relative = path.relative_to(site)
        if '.git' in relative.parts:
            continue
        assert not path.is_symlink(), 'Links não são aceitos no catálogo.'
        if path.is_file() and str(relative) not in ('PUBLICATION.sha256', 'PUBLICATION.sha256.asc'):
            actual[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, 'Arquivos adicionados, removidos ou alterados após a assinatura.'
    assert 'review.json' in actual
    print('PASS: assinatura oficial e conteúdo integral da publicação.')

if __name__ == '__main__':
    verify(*sys.argv[1:])
