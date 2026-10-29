"""Source preservation controls; no model or benchmark acceptance."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts/check_harness2_source.py'


class HarnessSourceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.vendor = self.root / 'third_party/harness2'
        self.vendor.mkdir(parents=True)
        self.original = b'original upstream\n'
        (self.vendor / 'README.md').write_bytes(self.original)
        blob = subprocess.check_output(['git', 'hash-object', '--stdin'], input=self.original).decode().strip()
        source = {'repository': 'fixture', 'revision': 'fixture', 'tree': 'fixture',
                  'files': {'README.md': blob}}
        (self.root / 'third_party/harness2.source.json').write_text(json.dumps(source))

    def run_check(self, code):
        result = subprocess.run([sys.executable, str(CHECK), '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout if code == 0 else result.stderr)

    def test_original_source_and_local_build_metadata(self):
        self.assertEqual(self.run_check(0)['files'], 1)
        generated = self.vendor / 'harness2.egg-info'
        generated.mkdir()
        (generated / 'PKG-INFO').write_text('local installation metadata')
        self.assertEqual(self.run_check(0)['proof_ceiling'], 'DECLARED_UPSTREAM_BYTES_ONLY')

    def test_modified_missing_and_extra_source_refused(self):
        file = self.vendor / 'README.md'
        file.write_bytes(b'changed\n')
        self.assertEqual(self.run_check(2)['error'], 'upstream_bytes_changed:README.md')
        file.unlink()
        self.assertEqual(self.run_check(2)['error'], 'upstream_file_inventory_changed')
        file.write_bytes(self.original)
        (self.vendor / 'extra.py').write_text('unexpected')
        self.assertEqual(self.run_check(2)['error'], 'upstream_file_inventory_changed')

    def test_symlink_refused(self):
        file = self.vendor / 'README.md'
        file.unlink()
        file.symlink_to(CHECK)
        self.assertEqual(self.run_check(2)['error'], 'upstream_symlink')
