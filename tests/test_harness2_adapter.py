import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from neoweaver.harness2_adapter import ReviewEvidenceAdapter
from neoweaver.harness_feedback import BehaviorLabel


class Harness2AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.request = self.ref('request.json', '{}')
        self.trace = self.ref('trace.ndjson', '{"fixture":"original action"}\n')
        self.snapshot = self.ref('trajectory.json', json.dumps({
            'kind': 'original_loop_behavior', 'request': self.request, 'sources': [self.trace],
            'native_traces': [self.trace], 'run_id': 'fixture-run', 'goal': 'Review the candidate.',
            'nodes': [], 'edges': [], 'findings': [], 'original_next': {'operation': 'readback'}}))

    def ref(self, name, text):
        p = self.root / name
        p.write_text(text)
        return {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

    def test_real_upstream_context_excludes_labels_and_preserves_trace(self):
        from harness2.core.context import build
        from harness2.core.spec import RunView
        label = BehaviorLabel('secret-eval-label', 'validation', 'pass', True, True, True, True)
        adapter = ReviewEvidenceAdapter(self.snapshot, (label,))
        tree = build(self.root / 'context', adapter, 'fixture-run',
                     [RunView('original', 'fixture-run', self.root, True, True)])
        text = '\n'.join(p.read_text() for p in tree.root.rglob('*') if p.is_file())
        self.assertIn('original action', text)
        self.assertNotIn('secret-eval-label', text)
        self.assertEqual(tree.failed, [])
        with self.assertRaises(RuntimeError):
            adapter.execute('fixture-run', None, 'replay')

    def test_real_upstream_judge_keeps_unknown_unscored(self):
        from harness2.core.judge import judge_one
        adapter = ReviewEvidenceAdapter(self.snapshot)
        result = judge_one(adapter, 'fixture-run', 'seq', 1, 'c1', 'fixture-run', self.root)
        self.assertFalse(result.graded)
        self.assertIsNone(result.frac)

    def test_real_upstream_judge_uses_only_reviewed_observations(self):
        from harness2.core.judge import judge_one
        label = BehaviorLabel('case', 'validation', 'fail', True, True, True, True)
        adapter = ReviewEvidenceAdapter(self.snapshot, (label,))
        result = judge_one(adapter, 'fixture-run', 'seq', 1, 'c1', 'fixture-run', self.root)
        self.assertTrue(result.graded)
        self.assertEqual(result.frac, 0)
        self.assertFalse(result.raw['authorizes_adoption'])

    def test_changed_source_is_refused(self):
        Path(self.trace['path']).write_text('changed')
        with self.assertRaises(ValueError):
            ReviewEvidenceAdapter(self.snapshot)

    def test_late_drift_cannot_receive_reward(self):
        from harness2.core.judge import judge_one
        label = BehaviorLabel('case', 'validation', 'pass', True, True, True, True)
        adapter = ReviewEvidenceAdapter(self.snapshot, (label,))
        Path(self.trace['path']).write_text('changed after construction')
        result = judge_one(adapter, 'fixture-run', 'seq', 1, 'c1', 'fixture-run', self.root)
        self.assertFalse(result.graded)
        self.assertIn('source drift', result.error)

    def test_json_owner_keeps_missing_review_unknown_and_binds_adjudication(self):
        from neoweaver.behavior_tools import inspect
        from dataclasses import asdict
        result = inspect(self.snapshot)
        self.assertEqual(result['status'], 'unknown')
        self.assertIsNone(result['upstream_judge']['fraction'])
        label = BehaviorLabel('case', 'validation', 'fail', True, True, True, True)
        review = self.ref('review.json', json.dumps({'schema': 1, 'snapshot': self.snapshot,
                         'reviewer': 'fixture observer', 'cases': [asdict(label)]}))
        result = inspect(self.snapshot, review)
        self.assertEqual(result['upstream_judge']['fraction'], 0)
        self.assertEqual(result['review'], review)
        foreign = self.ref('foreign.json', json.dumps({'schema': 1, 'snapshot': self.request,
                          'reviewer': 'fixture observer', 'cases': [asdict(label)]}))
        with self.assertRaises(ValueError):
            inspect(self.snapshot, foreign)
