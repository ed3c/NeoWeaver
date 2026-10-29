"""Source checks must reject omitted or altered upstream files before execution."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_harness2 import check_source


class Harness2SourceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        (self.root / 'LICENSE').write_text('original license\n')
        (self.root / 'benchmark.py').write_text('original benchmark\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Retain the fixture source')
        self.head = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args],
                              check=True, capture_output=True, text=True).stdout

    def test_intact_source(self):
        self.assertEqual(check_source(self.root, self.head), 2)

    def test_omitted_benchmark(self):
        (self.root / 'benchmark.py').unlink()
        with self.assertRaisesRegex(ValueError, 'file missing'):
            check_source(self.root, self.head)

    def test_assume_unchanged_cannot_hide_modified_source(self):
        self.git('update-index', '--assume-unchanged', 'benchmark.py')
        (self.root / 'benchmark.py').write_text('substituted benchmark\n')
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            check_source(self.root, self.head)

    def test_symlink_substitution(self):
        (self.root / 'benchmark.py').unlink()
        (self.root / 'benchmark.py').symlink_to(self.root / 'LICENSE')
        with self.assertRaisesRegex(ValueError, 'aliased'):
            check_source(self.root, self.head)

    def test_stale_head(self):
        with self.assertRaisesRegex(ValueError, 'HEAD differs'):
            check_source(self.root, '0' * 40)

    def test_extra_source(self):
        (self.root / 'extra.py').write_text('untracked')
        with self.assertRaisesRegex(ValueError, 'untracked'):
            check_source(self.root, self.head)


if __name__ == '__main__':
    unittest.main()
