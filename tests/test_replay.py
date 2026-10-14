"""A5 readback controls; deliberately not a native Snapshot Runner fixture."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from neoweaver.patches import OwnerRef
from neoweaver.replay import RunReadback, inspect_pair


def ref(name):
    return OwnerRef("original-owner", name)


def pair():
    shared = dict(snapshot_ref=ref("snapshot"), task_ref=ref("task"),
                  environment_ref=ref("environment"), solver_ref=ref("solver"),
                  seed_policy_ref=ref("seed-policy"), budget_ref=ref("budget"),
                  oracle_ref=ref("original-oracle"), terminal="completed",
                  effect_status="none_observed")
    return (RunReadback("baseline", **shared, harness_ref=ref("H0"),
                        run_ref=ref("run-A"), sandbox_ref=ref("sandbox-A"),
                        capture_ref=ref("capture-A"), completed=False),
            RunReadback("candidate", **shared, harness_ref=ref("H1"),
                        run_ref=ref("run-B"), sandbox_ref=ref("sandbox-B"),
                        capture_ref=ref("capture-B"), completed=True))


class ReplayReadbackTests(unittest.TestCase):
    def test_matched_original_conditions_do_not_grant_a_behavior_pass(self):
        result = inspect_pair(*pair())
        self.assertEqual(result.status, "STRUCTURALLY_COMPARABLE")
        self.assertEqual(result.reported_completion, (False, True))
        self.assertEqual(result.evidence_ceiling, "DECLARED_RUNNER_READBACKS_ONLY")
        self.assertFalse(result.authorizes_landing)
        self.assertNotEqual(result.status, "PASS")

    def test_every_fixed_condition_mismatch_is_inconclusive(self):
        baseline, candidate = pair()
        for field in ("snapshot_ref", "task_ref", "environment_ref", "solver_ref",
                      "seed_policy_ref", "budget_ref", "oracle_ref"):
            with self.subTest(field=field):
                altered = replace(candidate, **{field: ref("changed-" + field)})
                result = inspect_pair(baseline, altered)
                self.assertEqual(result.status, "INCONCLUSIVE")
                self.assertIn("unmatched_" + field, result.reasons)
                self.assertIsNone(result.reported_completion)

    def test_repeated_or_missing_run_sandbox_and_capture_ref_is_inconclusive(self):
        baseline, candidate = pair()
        for field in ("run_ref", "sandbox_ref", "capture_ref"):
            with self.subTest(field=field):
                repeated = inspect_pair(baseline, replace(candidate, **{field: getattr(baseline, field)}))
                absent = inspect_pair(baseline, replace(candidate, **{field: None}))
                self.assertEqual(repeated.status, "INCONCLUSIVE")
                self.assertEqual(absent.status, "INCONCLUSIVE")
                self.assertIn("reused_" + field, repeated.reasons)
                self.assertIn("missing_" + field, absent.reasons)

    def test_unknown_effect_or_missing_terminal_never_becomes_failure_or_zero(self):
        baseline, candidate = pair()
        unknown = inspect_pair(baseline, replace(candidate, effect_status="unknown"))
        partial = inspect_pair(baseline, replace(candidate, terminal="partial", completed=None))
        self.assertEqual(unknown.status, "INCONCLUSIVE")
        self.assertIn("candidate.unknown_effect", unknown.reasons)
        self.assertEqual(partial.status, "INCONCLUSIVE")
        self.assertIn("candidate.missing_terminal_result", partial.reasons)
        self.assertIsNone(unknown.reported_completion)
        self.assertIsNone(partial.reported_completion)

    def test_no_treatment_difference_is_not_invented_as_gain(self):
        baseline, candidate = pair()
        observed = inspect_pair(baseline, replace(candidate, harness_ref=baseline.harness_ref,
                                                  completed=False))
        self.assertEqual(observed.reported_completion, (False, False))
        self.assertEqual(observed.status, "STRUCTURALLY_COMPARABLE")

    def test_malformed_identity_and_impossible_state_refuse(self):
        baseline, candidate = pair()
        for value, code in (
            (replace(candidate, arm="baseline"), "wrong_arm_order"),
            (replace(candidate, task_ref=OwnerRef("", "task")), "candidate.task_ref.invalid_ref"),
            (replace(candidate, completed=1), "candidate.invalid_completion"),
            (replace(candidate, terminal="unrecognized"), "candidate.invalid_terminal"),
            (replace(candidate, terminal="partial", completed=True), "candidate.nonterminal_completion"),
            (replace(candidate, effect_status="pass"), "candidate.invalid_effect_status"),
            (replace(candidate, capture_ref="path-to-capture"), "candidate.capture_ref.invalid_ref"),
        ):
            with self.subTest(code=code):
                outcome = inspect_pair(baseline, value)
                self.assertEqual(outcome.status, "REFUSED")
                self.assertEqual(outcome.reasons, (code,))
        self.assertEqual(inspect_pair({}, candidate).status, "REFUSED")

    def test_missing_fixed_references_are_gaps_but_malformed_references_refuse(self):
        baseline, candidate = pair()
        for field in ("snapshot_ref", "task_ref", "environment_ref", "solver_ref",
                      "seed_policy_ref", "budget_ref", "oracle_ref", "harness_ref"):
            with self.subTest(field=field):
                report = inspect_pair(baseline, replace(candidate, **{field: None}))
                self.assertEqual(report.status, "INCONCLUSIVE")
                self.assertIn("candidate.missing_" + field, report.reasons)

    def test_readback_inspection_has_no_file_process_or_network_effects(self):
        with patch("builtins.open", side_effect=AssertionError("read")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("socket.socket", side_effect=AssertionError("network")):
            self.assertEqual(inspect_pair(*pair()).status, "STRUCTURALLY_COMPARABLE")


if __name__ == "__main__":
    unittest.main()
