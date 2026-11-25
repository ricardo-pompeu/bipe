import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import importlib.util
spec = importlib.util.spec_from_file_location('publication', Path(__file__).resolve().parents[1]/'scripts/verificar-publicacao.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        (self.site/'review.json').write_text('{}')
        digest = hashlib.sha256(b'{}').hexdigest()
        (self.site/'PUBLICATION.sha256').write_text(digest+'  review.json\n')
        result = subprocess.CompletedProcess([], 0, stdout='[GNUPG:] VALIDSIG '+module.FINGERPRINT+' 2026-11-25\n')
        self.mock = patch.object(module.subprocess, 'run', return_value=result)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_exact_files(self):
        verify(self.site, self.site/'public.asc')

    def test_tampered_and_extra_files(self):
        (self.site/'review.json').write_text('changed')
        with self.assertRaises(AssertionError): verify(self.site, self.site/'public.asc')
        (self.site/'review.json').write_text('{}')
        (self.site/'extra').write_text('unreviewed')
        with self.assertRaises(AssertionError): verify(self.site, self.site/'public.asc')

    def test_symlink_rejected(self):
        (self.site/'link').symlink_to('/etc/passwd')
        with self.assertRaises(AssertionError): verify(self.site, self.site/'public.asc')

    def test_path_escape_rejected(self):
        (self.site/'PUBLICATION.sha256').write_text('0'*64+'  ../escape\n')
        with self.assertRaises(AssertionError): verify(self.site, self.site/'public.asc')

    def test_wrong_signer_rejected(self):
        module.subprocess.run.return_value.stdout='[GNUPG:] VALIDSIG '+'0'*40+' 2026-11-25\n'
        with self.assertRaises(AssertionError): verify(self.site, self.site/'public.asc')
