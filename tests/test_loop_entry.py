"""Carrier-only tests; mocked launches are not native Loop observations."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('loop_entry', ROOT / 'scripts/loop.py')
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)


class LoopEntryTests(unittest.TestCase):
    def request(self, path, **changes):
        value = {'schema': 1, 'repository': str(ROOT), 'mode': 'inner-only',
                 'goal': 'Carrier control only', 'write_paths': ['tests/test_loop_entry.py'],
                 'acceptance': ['Preserve original request bytes'], 'source_refs': [],
                 'selected_skill': 'owner-selected-skill', 'model': 'owner-selected-model'}
        value.update(changes)
        path.write_text(json.dumps(value))
        return path.read_bytes()

    def test_forwards_unchanged_request_once_and_returns_original_status(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'request with spaces.json'
            before = self.request(path, mode='outer-only')
            with patch.object(entry.subprocess, 'run', return_value=subprocess.CompletedProcess([], 7)) as run:
                self.assertEqual(entry.enter(path, '/owner/soodles'), 7)
            run.assert_called_once_with(
                ['/owner/soodles', 'loop', 'enter', '--request-file', str(path.resolve())],
                cwd=ROOT, check=False,
            )
            self.assertEqual(path.read_bytes(), before)

    def test_wrong_repository_and_schema_refuse_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'request.json'
            for changes in ({'repository': td}, {'repository': '.'},
                            {'schema': 2}, {'schema': True}):
                with self.subTest(changes=changes):
                    self.request(path, **changes)
                    with patch.object(entry.subprocess, 'run') as run:
                        with self.assertRaises(ValueError):
                            entry.enter(path)
                        run.assert_not_called()

    def test_duplicate_fields_refuse_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'request.json'
            path.write_text('{"schema": 1, "schema": 1}')
            with patch.object(entry.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'duplicate_request_field'):
                    entry.enter(path)
                run.assert_not_called()

    def test_semantic_fields_are_validated_only_by_original_cli(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'request.json'
            self.request(path, mode='invalid-owner-must-refuse')
            with patch.object(entry.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2)) as run:
                self.assertEqual(entry.enter(path), 2)
            run.assert_called_once()
