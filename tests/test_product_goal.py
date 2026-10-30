"""Synthetic original-owner controls, never Native acceptance receipts."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from neoweaver.product_cli import execute

ROOT = Path(__file__).resolve().parents[1]


def ref(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class ProductFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / 'product'
        (self.repo / 'docs/specs').mkdir(parents=True)
        (self.repo / 'docs/compiled').mkdir()
        for relative in ('docs/specs/neoweaver-product-program.md', 'docs/compiled/specification.json'):
            (self.repo / relative).write_bytes((ROOT / relative).read_bytes())
        self.request_path = self.base / 'request.json'
        self.request_path.write_text(json.dumps({'repository': str(self.repo), 'goal': 'original admitted local task'}))
        self.request_bytes = self.request_path.read_bytes()
        self.request = ref(self.request_path)
        self.acceptance = self.base / 'acceptance.json'
        self.acceptance.write_text(json.dumps({'head': 'synthetic-owner-head-not-native'}))
        self.result = {'owner': 'soodles.loop', 'request': self.request, 'status': 'running', 'inner': {},
                       'next': {'tool': 'soodles_loop_enter', 'arguments': {'request_file': str(self.request_path)}}}
        self.readback_path = self.base / 'readback.json'
        self.save_result(self.result)
        self.selection = {'profile': 'neoweaver', 'repository': str(self.repo),
                          'goal': ref(self.repo / 'docs/specs/neoweaver-product-program.md'),
                          'requirements': ref(self.repo / 'docs/compiled/specification.json'),
                          'tasks': {'A': {'request': self.request, 'readback': ref(self.readback_path)}},
                          'coverage': [{'requirement': 'REQ-trainability', 'clause': 'local parser boundary only',
                                        'task': 'A', 'relation': 'product'}]}

    def save_result(self, result, name=None):
        path = self.base / name if name else self.readback_path
        path.write_text(json.dumps(result))
        return ref(path)

    def integrated(self):
        result = deepcopy(self.result)
        result['next'] = None
        result['inner'] = {'review_progress': {'status': 'locally_integrated'},
                           'acceptance_report': {'status': 'PASS', 'scope': 'integrated',
                                                 'record': ref(self.acceptance)}}
        return result

    def arguments(self, operation='goal_reconcile', **extra):
        return execute(operation, {'selection': self.selection, **extra})


class ProductGoalTests(ProductFixture):
    def test_original_full_goal_and_cards_survive_local_completion(self):
        previous = self.selection['tasks']['A']['readback']
        self.selection['baseline'] = {'A': previous}
        current = self.save_result(self.integrated(), 'new-readback.json')
        self.selection['tasks']['A']['readback'] = current
        output = self.arguments()
        self.assertEqual(output['locally_completed'][0]['clause'], 'local parser boundary only')
        self.assertEqual(output['changes'][0]['before'], 'pending')
        self.assertEqual(output['changes'][0]['after'], 'locally_completed')
        self.assertEqual(len(output['remaining_requirements']), 10)
        self.assertEqual(len(output['knowledge_record']['cards']), 44)
        self.assertIn('Migration-RL', output['goal']['text'])
        self.assertIn('文章', output['goal']['text'])
        self.assertEqual(output['whole_goal'], 'OPEN')
        self.assertFalse(output['authorizes_landing'])

    def test_blocked_pending_missing_and_forged_pass_are_distinct(self):
        cases = [('blocked', {'status': 'blocked'}, 'blocked'),
                 ('writer', {'status': 'completed'}, 'pending_verification'),
                 ('forged', {'status': 'PASS'}, 'pending')]
        for label, delta, expected in cases:
            self.selection['tasks']['A']['readback'] = self.save_result({**self.result, **delta}, label + '.json')
            output = self.arguments()
            self.assertEqual(output['obligations'][0]['status'], expected)
            self.assertEqual(output['locally_completed'], [])
        del self.selection['tasks']['A']['readback']
        output = self.arguments()
        self.assertEqual(output['unknown'][0]['task'], 'A')
        self.assertEqual(output['needs_input'][0]['name'], 'owner_readback')

    def test_semantic_choice_returns_evidence_and_schema(self):
        del self.selection['coverage']
        output = self.arguments()
        self.assertEqual(output['status'], 'needs_input')
        self.assertEqual(output['needs_input'][0]['name'], 'goal_coverage')
        self.assertIn('REQ-trainability', output['needs_input'][0]['input_schema']['items']['properties']['requirement']['enum'])
        self.assertEqual(output['next']['A'], self.result['next'])
        self.assertIn('A', output['owner_states'])

    def test_wrong_goal_repo_and_source_drift_refused(self):
        original = deepcopy(self.selection)
        self.selection['goal'] = self.selection['requirements']
        self.assertIn('wrong_neoweaver_goal_source', self.arguments()['problem'])
        self.selection = deepcopy(original)
        other = self.base / 'task-repository'
        other.mkdir()
        self.request_path.write_text(json.dumps({'repository': str(other)}))
        self.selection['tasks']['A']['request'] = ref(self.request_path)
        self.assertIn('task_product_repository_mismatch', self.arguments()['problem'])
        self.selection = original
        self.assertIn('source_changed', self.arguments()['problem'])

    def test_readback_and_acceptance_record_drift_refused(self):
        self.selection['tasks']['A']['readback'] = self.save_result(self.integrated())
        self.acceptance.write_text('{"head":"changed"}')
        self.assertEqual(self.arguments()['status'], 'refused')
        self.readback_path.write_text('{}')
        self.assertIn('source_changed', self.arguments()['problem'])

    def test_dependency_is_never_product_completion(self):
        self.selection['coverage'][0]['relation'] = 'dependency'
        self.selection['tasks']['A']['readback'] = self.save_result(self.integrated())
        output = self.arguments()
        self.assertEqual(output['locally_completed'], [])
        self.assertEqual(len(output['dependency_completed']), 1)

    def test_generic_profile_does_not_require_neoweaver_counts(self):
        path = self.repo / 'small.json'
        path.write_text(json.dumps({'requirements': [{'id': 'R', 'statement': 'keep small'}]}))
        self.selection.update(profile='generic', requirements=ref(path), tasks={}, coverage=[])
        output = self.arguments()
        self.assertEqual(len(output['remaining_requirements']), 1)
        self.assertEqual(output['whole_goal'], 'OPEN')

    def test_dry_run_without_live_carrier_and_refresh_reports_missing_capability(self):
        output = self.arguments('task_continue', task='A', capture=str(self.base / 'unused'), dry_run=True)
        self.assertEqual(output['status'], 'dry_run')
        self.assertFalse((self.base / 'unused').exists())
        output = self.arguments('goal_refresh', capture=str(self.base / 'unavailable'))
        self.assertEqual(output['status'], 'needs_input')
        self.assertIn('original_carrier', [i['name'] for i in output['needs_input']])
        self.assertFalse((self.base / 'unavailable').exists())

    def test_foreign_owner_and_forged_schema_are_refused(self):
        self.selection['tasks']['A']['readback'] = self.save_result({**self.result, 'owner': 'product.fake'})
        self.assertIn('foreign_task_owner', self.arguments()['problem'])
        self.selection['tasks']['A']['readback'] = self.save_result(self.result)
        self.selection['coverage'][0]['status'] = 'PASS'
        self.assertIn('unexpected_field', self.arguments()['problem'])


if __name__ == '__main__':
    unittest.main()
