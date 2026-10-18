import unittest
from dataclasses import replace

from neoweaver.harness_feedback import BehaviorLabel, dataset, paired_feedback
from neoweaver.replay import PairInspection


class HarnessFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.good = BehaviorLabel('original-review', 'validation', 'pass', True, True, True, True)
        self.pair = PairInspection('STRUCTURALLY_COMPARABLE', (), (True, True))

    def test_negative_is_preserved_and_unknown_is_not_zero(self):
        rows = dataset((replace(self.good, outcome='fail'),
                        replace(self.good, case_id='missing', outcome='unknown')))['cases']
        self.assertEqual(rows[0]['status'], 'golden_eligible')
        self.assertEqual(rows[0]['reward'], 0)
        self.assertEqual(rows[1]['status'], 'candidate')
        self.assertIsNone(rows[1]['reward'])

    def test_unobserved_or_self_review_is_not_golden(self):
        for field in ('criteria_supported', 'independent_review', 'native_observed'):
            result = dataset((replace(self.good, **{field: False}),))
            self.assertEqual(result['cases'][0]['status'], 'candidate')
            self.assertIsNone(result['cases'][0]['reward'])

    def test_same_result_is_noop_not_forced_adoption(self):
        result = paired_feedback(self.pair, (self.good,), (self.good,))
        self.assertEqual(result['status'], 'NOOP')
        self.assertEqual(result['recommendation'], 'retain_baseline')
        self.assertFalse(result['authorizes_adoption'])

    def test_improvement_still_needs_outer_review(self):
        result = paired_feedback(self.pair, (replace(self.good, outcome='fail'),), (self.good,))
        self.assertEqual(result['reward_delta'], 1)
        self.assertEqual(result['recommendation'], 'outer_review_required')
        self.assertFalse(result['authorizes_training'])

    def test_cost_cannot_override_hard_gate(self):
        result = paired_feedback(self.pair, (self.good,), (replace(self.good, hard_gates=False),))
        self.assertEqual(result['status'], 'REJECTED')
        self.assertIsNone(result['reward_delta'])

    def test_unknown_neighbor_cannot_hide_known_hard_gate_failure(self):
        result = paired_feedback(self.pair, (self.good, replace(self.good, case_id='unknown')),
            (replace(self.good, hard_gates=False), replace(self.good, case_id='unknown', outcome='unknown')))
        self.assertEqual(result['status'], 'REJECTED')
        self.assertEqual(result['reasons'], ['candidate_hard_gate_failure'])

    def test_positive_average_cannot_hide_regression(self):
        base = (self.good, replace(self.good, case_id='b', outcome='fail'), replace(self.good, case_id='c', outcome='fail'))
        candidate = (replace(self.good, outcome='fail'), replace(self.good, case_id='b'), replace(self.good, case_id='c'))
        result = paired_feedback(self.pair, base, candidate)
        self.assertGreater(result['reward_delta'], 0)
        self.assertEqual(result['status'], 'REJECTED')

    def test_missing_pair_and_population_and_heldout_remain_inconclusive(self):
        for pair, baseline, candidate in [
            (PairInspection('INCONCLUSIVE', ('budget_missing',), None), (self.good,), (self.good,)),
            (self.pair, (), ()),
            (self.pair, (self.good,), (replace(self.good, case_id='other'),)),
            (self.pair, (replace(self.good, partition='held_out'),), (replace(self.good, partition='held_out'),)),
            (self.pair, (self.good,), (replace(self.good, hard_gates=None),))]:
            self.assertEqual(paired_feedback(pair, baseline, candidate)['status'], 'INCONCLUSIVE')

    def test_duplicate_and_invalid_labels_refuse(self):
        for labels in [(self.good, self.good), (replace(self.good, native_observed='true'),),
                       (replace(self.good, outcome='excellent'),)]:
            with self.assertRaises(ValueError):
                dataset(labels)
