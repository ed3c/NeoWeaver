"""Public native-to-original-pair controls using labeled protocol fixtures."""
from dataclasses import replace
from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from neoweaver.native import DecisionOracle, FixedConditions, inspect_native_pair
from neoweaver.patches import OwnerRef
from neoweaver.replay import inspect_pair
from test_native import NativeFixture, ANSWER, POPULATION


class NativePairTests(NativeFixture, unittest.TestCase):
    def test_distinct_matching_native_results_keep_unknown_effects_and_isolation(self):
        baseline = self.capture(thread='fixture-A')
        candidate = self.capture(arm='candidate', thread='fixture-B')
        with patch('neoweaver.native.inspect_pair', wraps=inspect_pair) as original:
            report = inspect_native_pair(baseline, candidate, self.oracle)
        self.assertEqual(original.call_count, 1)
        self.assertEqual([r.status for r in report.oracle_results], ['MATCH_SCOPED', 'MATCH_SCOPED'])
        self.assertEqual(report.pair.status, 'INCONCLUSIVE')
        self.assertEqual(report.pair.reasons, ('missing_sandbox_ref', 'baseline.unknown_effect', 'candidate.unknown_effect'))
        self.assertEqual(report.treatment, 'CONTROL_H0_H0')
        self.assertEqual(report.launch_mismatches, ())
        self.assertIsNone(report.pair.reported_completion)
        for readback in report.readbacks:
            self.assertEqual(readback.completed, True)
            self.assertIsNone(readback.sandbox_ref)
            self.assertEqual(readback.effect_status, 'unknown')
        self.assertFalse(report.authorizes_training)
        self.assertFalse(report.authorizes_landing)

    def test_every_actual_launch_mismatch_is_named_despite_equal_declared_refs(self):
        baseline = self.capture(thread='fixture-A')
        alternatives = dict(executable=Path('/usr/bin/false'), model='other-model', effort='low',
                            prompt=b'Different request', response_schema=b'{"type":"object","title":"different"}',
                            population=POPULATION.replace(b'fixture one', b'different input'),
                            timeout_seconds=31, seed_policy='different policy')
        for field, value in alternatives.items():
            with self.subTest(field=field):
                candidate = self.capture(arm='candidate', thread='fixture-B', task=replace(self.task, **{field:value}))
                report = inspect_native_pair(baseline, candidate, self.oracle)
                self.assertEqual(report.pair.status, 'INCONCLUSIVE')
                self.assertIn('unmatched_launch_' + field, report.launch_mismatches)
                self.assertIn('unmatched_launch_' + field, report.pair.reasons)
                self.assertEqual(report.oracle_results[1].reasons, ('oracle_task_mismatch',))

    def test_conditions_are_from_each_launch_not_common_posthoc_values(self):
        baseline = self.capture(thread='fixture-A')
        for field in ('snapshot_ref','task_ref','environment_ref','solver_ref','seed_policy_ref','budget_ref'):
            with self.subTest(field=field):
                candidate = self.capture(arm='candidate', thread='fixture-B',
                    conditions=replace(self.conditions, **{field:OwnerRef('fixture','different')}))
                report = inspect_native_pair(baseline, candidate, self.oracle)
                self.assertIn('unmatched_' + field, report.pair.reasons)
                self.assertEqual(getattr(report.readbacks[1], field), OwnerRef('fixture','different'))

    def test_missing_original_conditions_remain_named_gaps(self):
        baseline = self.capture(thread='fixture-A', conditions=FixedConditions())
        candidate = self.capture(arm='candidate', thread='fixture-B', conditions=FixedConditions())
        report = inspect_native_pair(baseline, candidate, replace(self.oracle, reference=None))
        self.assertEqual(report.pair.status, 'INCONCLUSIVE')
        for arm in ('baseline','candidate'):
            for field in ('snapshot_ref','task_ref','environment_ref','solver_ref','seed_policy_ref','budget_ref','oracle_ref','harness_ref'):
                self.assertIn(arm + '.missing_' + field, report.pair.reasons)
        self.assertEqual([r.status for r in report.oracle_results], ['MATCH_SCOPED','MATCH_SCOPED'])

    def test_reused_capture_and_run_and_wrong_arm_order(self):
        baseline = self.capture()
        candidate = self.capture(arm='candidate')
        self.assertIn('reused_run_ref', inspect_native_pair(baseline,candidate,self.oracle).pair.reasons)
        reused = replace(baseline, arm='candidate')
        report = inspect_native_pair(baseline,reused,self.oracle)
        self.assertEqual(report.oracle_results[1].reasons, ('capture_drift',))
        self.assertIn('reused_capture_ref', report.pair.reasons)
        self.assertEqual(inspect_native_pair(candidate,baseline,self.oracle).pair.status, 'REFUSED')

    def test_different_source_lineage_is_explicit_even_with_identical_manifests(self):
        baseline = self.capture(thread='fixture-A')
        self.pair = replace(self.pair, commit='c' * 40)
        candidate = self.capture(arm='candidate', thread='fixture-B')
        report = inspect_native_pair(baseline,candidate,self.oracle)
        self.assertIn('unmatched_source_pair',report.launch_mismatches)
        self.assertEqual(report.treatment,'UNKNOWN')

    def test_fixed_oracle_is_bound_to_result_and_cannot_be_substituted_as_verdict(self):
        baseline = self.capture(thread='fixture-A')
        candidate = self.capture(arm='candidate',thread='fixture-B')
        wrong = DecisionOracle(self.task, ANSWER.replace(b'duplicate_json_key',b'wrong_condition'), OwnerRef('fixture','other-oracle'))
        report = inspect_native_pair(baseline,candidate,wrong)
        self.assertEqual([r.status for r in report.oracle_results],['FAIL_SCOPED','FAIL_SCOPED'])
        self.assertTrue(all(r.oracle is wrong for r in report.oracle_results))
        self.assertEqual(report.readbacks[0].oracle_ref,wrong.reference)
        empty = inspect_native_pair(baseline,candidate,replace(self.oracle,expected=b'{"decisions":[]}'))
        self.assertEqual(empty.oracle_results[0].reasons,('case_population_mismatch',))


class DriverPreflightTests(unittest.TestCase):
    def test_relative_and_traversal_evidence_roots_cannot_enter_repository(self):
        from scripts import run_native_parser_control as driver
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            repository = root / 'repo'
            repository.mkdir()
            sibling = root / 'sibling'
            sibling.mkdir()
            selection = root / 'task.json'
            destinations = (repository / 'evidence',
                            sibling / '..' / 'repo' / 'evidence',
                            Path(os.path.relpath(repository / 'evidence', Path.cwd())))
            for destination in destinations:
                with self.subTest(destination=destination):
                    selection.write_text(json.dumps({'selected_native_task': {'evidence_root': str(destination)}}))
                    with patch.object(driver, '__file__', str(repository / 'scripts' / 'driver.py')), \
                         patch('sys.argv', ['driver', str(selection), 'a' * 40]), \
                         patch.object(driver, 'read_pinned') as read, \
                         patch.object(driver, 'run_native_arm') as launch, \
                         self.assertRaisesRegex(ValueError, 'evidence root overlaps repository'):
                        driver.main()
                    read.assert_not_called()
                    launch.assert_not_called()
                    self.assertFalse((repository / 'evidence').exists())


if __name__ == '__main__':
    unittest.main()
