#!/usr/bin/python3
"""Mudanças de acesso do aplicativo exigem atualização explícita desta política."""
import json
from pathlib import Path
manifest = json.loads(Path('io.github.ricardo_pompeu.Bipe.json').read_text())
assert manifest['app-id'] == 'io.github.ricardo_pompeu.Bipe'
assert set(manifest['finish-args']) == {'--socket=cups', '--share=ipc', '--socket=wayland', '--socket=fallback-x11', '--device=dri'}, 'Permissões alteradas: revisão humana necessária.'
assert not list(Path('.github/workflows').glob('*pull_request_target*'))
for path in Path('.github/workflows').glob('*.yml'):
    text = path.read_text()
    assert 'pull_request_target' not in text
    assert 'secrets.' not in text, 'Esta infraestrutura mantém credenciais de assinatura fora do CI.'
print('PASS: identidade, permissões previstas e ausência de segredos de assinatura nos workflows.')
