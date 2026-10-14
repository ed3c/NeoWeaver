"""A6 direct decision screening: neither FileRefs nor Provider-auth fixtures."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from neoweaver.learning import TrainingCandidate, inspect_training_candidate


def sample(actor="proposer", method="sft"):
    return TrainingCandidate(
        actor=actor, method=method, partition="train", rights="allowed",
        acceptance="pass", protected_regressions="pass", effect_status="none_observed",
        lineage="matched", token_provenance="available",
        replay="observed", verifier="independent", reward="observed",
    )


class LearningEligibilityTests(unittest.TestCase):
    def test_supplied_normal_facts_do_not_authorize_training(self):
        result = inspect_training_candidate(sample())
        self.assertEqual(result.status, "STRUCTURALLY_ELIGIBLE")
        self.assertEqual(result.evidence_ceiling, "SUPPLIED_FACTS_ONLY")
        self.assertFalse(result.eligible_for_training)
        self.assertFalse(result.authorizes_landing)
        self.assertEqual(result.reasons, ())

    def test_sft_proposer_does_not_require_fake_generated_tokens(self):
        for provenance in ("missing", "unknown"):
            with self.subTest(provenance=provenance):
                case = replace(sample(), token_provenance=provenance)
                self.assertEqual(inspect_training_candidate(case).status, "STRUCTURALLY_ELIGIBLE")

    def test_gradient_and_open_solver_require_real_token_provenance(self):
        for case in (replace(sample(method="policy_gradient"), token_provenance="missing"),
                     replace(sample("open_solver"), token_provenance="unknown")):
            with self.subTest(case=case):
                result = inspect_training_candidate(case)
                self.assertEqual(result.status, "INCONCLUSIVE")
                self.assertIn("token_provenance_unavailable", result.reasons)
                self.assertFalse(result.eligible_for_training)

    def test_frozen_codex_never_enters_trainable_policy(self):
        result = inspect_training_candidate(sample("frozen_codex"))
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("frozen_codex_not_trainable", result.reasons)

    def test_validation_heldout_and_denied_rights_block(self):
        for field, value, expected in (
                ("partition", "validation", "non_training_partition"),
                ("partition", "held_out", "non_training_partition"),
                ("rights", "denied", "rights_denied")):
            with self.subTest(field=field, value=value):
                result = inspect_training_candidate(replace(sample(), **{field: value}))
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn(expected, result.reasons)

    def test_acceptance_and_protected_regression_failures_precede_cost(self):
        case = replace(sample(), acceptance="fail", protected_regressions="fail")
        result = inspect_training_candidate(case)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(set(result.reasons),
                         {"acceptance_failed", "protected_regression_failed"})

    def test_replay_failure_and_wrong_lineage_are_not_silent_success(self):
        case = replace(sample(), replay="failed", lineage="mismatched")
        result = inspect_training_candidate(case)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(set(result.reasons), {"replay_failed", "lineage_mismatch"})

    def test_self_verifier_cannot_claim_independent_acceptance(self):
        result = inspect_training_candidate(replace(sample(), verifier="self"))
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("self_reported_verifier", result.reasons)

    def test_undetermined_results_and_effects_remain_unknown(self):
        for field in ("partition", "rights", "acceptance", "protected_regressions",
                      "effect_status", "lineage", "replay", "verifier", "reward"):
            with self.subTest(field=field):
                case = replace(sample(), **{field: "unknown"})
                result = inspect_training_candidate(case)
                self.assertEqual(result.status, "INCONCLUSIVE")
                self.assertIn(field + "_unknown", result.reasons)

    def test_known_hard_gate_blocks_despite_other_unknowns(self):
        case = replace(sample(), partition="held_out", rights="unknown",
                       acceptance="unknown", effect_status="unknown")
        result = inspect_training_candidate(case)
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("non_training_partition", result.reasons)

    def test_no_file_ref_or_provider_identity_selection_in_public_input(self):
        keys = set(TrainingCandidate.__dataclass_fields__)
        self.assertEqual(keys, {
            "actor", "method", "partition", "rights", "acceptance",
            "protected_regressions", "effect_status", "lineage",
            "token_provenance", "replay", "verifier", "reward",
        })
        self.assertFalse(any("ref" in key or "provider" in key for key in keys))

    def test_malformed_statuses_or_freeform_identities_are_refused(self):
        self.assertEqual(inspect_training_candidate(None).status, "REFUSED")
        bad = (replace(sample(), actor="another-owner"),
               replace(sample(), method="guess"),
               replace(sample(), rights=True),
               replace(sample(), replay="pass"),
               replace(sample(), token_provenance=1))
        for candidate in bad:
            with self.subTest(candidate=candidate):
                self.assertEqual(inspect_training_candidate(candidate).status, "REFUSED")

    def test_inspection_is_pure_without_file_process_network_effects(self):
        with patch("builtins.open", side_effect=AssertionError("file")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("socket.socket", side_effect=AssertionError("network")):
            self.assertEqual(inspect_training_candidate(sample()).status,
                             "STRUCTURALLY_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
