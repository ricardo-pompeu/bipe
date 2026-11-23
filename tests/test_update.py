from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


class UpdateTest(unittest.TestCase):
    def test_installs_and_updates_same_scope_without_cups(self):
        root = Path(__file__).resolve().parents[1]
        for scope in ('fresh', 'user', 'system', 'both'):
            with self.subTest(scope=scope), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                for script in ('atualizar-bipe.sh', 'instalar-bipe.sh'):
                    shutil.copy(root / 'scripts' / script, folder)
                (folder / 'Bipe.flatpak').write_bytes(b'test bundle')
                log = folder / 'log'
                code = f'#!{sys.executable}\n' + '''
import os, sys
from pathlib import Path
name = Path(sys.argv[0]).name
args = sys.argv[1:]
if name == 'id':
    print('1000')
elif name == 'flatpak':
    with open(os.environ['LOG'], 'a') as log:
        print(*args, file=log)
    if args[0] == 'info':
        if 'org.gnome.Platform' in args[-1]:
            sys.exit(0)
        scope = os.environ['SCOPE']
        sys.exit(0 if scope == 'both' or '--' + scope in args else 1)
'''
                for name in ('id', 'flatpak'):
                    p = folder / name
                    p.write_text(code)
                    p.chmod(0o755)
                env = {**os.environ, 'PATH': f'{folder}:/usr/bin:/bin', 'LOG': str(log), 'SCOPE': scope}
                script = 'atualizar-bipe.sh' if scope == 'fresh' else 'instalar-bipe.sh'
                result = subprocess.run(['sh', str(folder / script)], env=env, capture_output=True, text=True)
                calls = log.read_text()
                if scope == 'both':
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('install ', calls)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    target = 'system' if scope == 'system' else 'user'
                    self.assertIn(f'install --{target} --bundle --or-update --noninteractive', calls)
                    self.assertNotIn('lpadmin', calls)
                    self.assertEqual('--reinstall' in calls, scope != 'fresh')
