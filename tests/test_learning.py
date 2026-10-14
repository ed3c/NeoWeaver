"""A6 declared lineage discriminators; no model trainer or native dataset."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from neoweaver.learning import (
    GenerationEvidence, EvaluationEvidence, TrainingCandidate, inspect_training_candidate
)
from neoweaver.patches import OwnerRef


def ref(name, producer="original-generation"):
    return OwnerRef(producer, name)


def sample(actor="proposer", method="sft"):
    generation = GenerationEvidence(actor, ref("policy"), ref("observation"), ref("action"),
                                    ref("generation"), ref("own-tokens"))
    evaluation = EvaluationEvidence(ref("observation"), ref("action"), ref("rollout", "original-runner"),
                                    ref("replay", "original-runner"), ref("verification", "independent-verifier"),
                                    ref("protected-oracle", "original-oracle"), ref("reward", "original-reward"),
                                    "pass", "pass", "none_observed")
    return TrainingCandidate(generation, evaluation, "train", "allowed", method,
                             ref("rights", "original-rights-owner"), ref("split", "original-dataset-owner"))


class LearningEligibilityTests(unittest.TestCase):
    def test_honest_proposer_source_declarations_are_only_structurally_eligible(self):
        result = inspect_training_candidate(sample())
        self.assertEqual(result.status, "STRUCTURALLY_ELIGIBLE")
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.evidence_ceiling, "DECLARED_EVIDENCE_RELATIONS_ONLY")
        self.assertFalse(result.eligible_for_training)
        self.assertFalse(result.authorizes_landing)

    def test_proposer_sft_allows_missing_token_only_for_non_gradient_method(self):
        record = sample()
        sft = replace(record, generation=replace(record.generation, token_ref=None))
        self.assertEqual(inspect_training_candidate(sft).status, "STRUCTURALLY_ELIGIBLE")
        pg = replace(sft, method="policy_gradient")
        result = inspect_training_candidate(pg)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("generation.token_ref.missing", result.reasons)

    def test_open_solver_requires_own_token_lineage_even_for_sft(self):
        record = sample("open_solver")
        missing = replace(record, generation=replace(record.generation, token_ref=None))
        result = inspect_training_candidate(missing)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("generation.token_ref.missing", result.reasons)
        self.assertEqual(inspect_training_candidate(record).status, "STRUCTURALLY_ELIGIBLE")

    def test_frozen_codex_never_eligible_even_with_fabricated_own_tokens(self):
        result = inspect_training_candidate(sample("frozen_codex"))
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("frozen_codex_not_trainable", result.reasons)

    def test_validation_and_held_out_never_enter_training(self):
        for partition in ("validation", "held_out"):
            with self.subTest(partition=partition):
                result = inspect_training_candidate(replace(sample(), partition=partition))
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn("non_training_partition", result.reasons)

    def test_rights_denial_and_hard_gate_failure_cannot_be_rewarded_away(self):
        original = sample()
        broken = replace(original, rights="denied",
                         evaluation=replace(original.evaluation, acceptance="fail", protected_regressions="fail"))
        result = inspect_training_candidate(broken)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(set(result.reasons), {"rights_denied", "acceptance_failed", "protected_regression_failed"})

    def test_unknown_rights_or_oracle_or_effect_remain_inconclusive(self):
        original = sample()
        unknown = replace(original, rights="unknown", partition="unknown",
                          evaluation=replace(original.evaluation, acceptance="unknown", protected_regressions="unknown",
                                             effect_status="unknown", reward_ref=None))
        result = inspect_training_candidate(unknown)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("rights_unknown", result.reasons)
        self.assertIn("partition_unknown", result.reasons)
        self.assertIn("external_effect_unknown", result.reasons)
        self.assertIn("evaluation.reward_ref.missing", result.reasons)
        self.assertFalse(result.eligible_for_training)

    def test_lineage_must_match_same_observation_and_action(self):
        original = sample()
        for field, why in (("observation_ref", "observation_lineage_mismatch"),
                           ("action_ref", "action_lineage_mismatch")):
            with self.subTest(field=field):
                record = replace(original, evaluation=replace(original.evaluation, **{field: ref("foreign")}))
                result = inspect_training_candidate(record)
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn(why, result.reasons)

    def test_self_reported_verifier_is_not_independent_evidence(self):
        original = sample()
        changed = replace(original, evaluation=replace(original.evaluation,
                                                      verifier_ref=ref("self-verification")))
        result = inspect_training_candidate(changed)
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("self_reported_verifier", result.reasons)

    def test_missing_rollout_replay_or_original_oracle_cannot_create_reward(self):
        original = sample()
        for field in ("rollout_ref", "replay_ref", "verifier_ref", "oracle_ref", "reward_ref"):
            with self.subTest(field=field):
                record = replace(original, evaluation=replace(original.evaluation, **{field: None}))
                result = inspect_training_candidate(record)
                self.assertEqual(result.status, "INCONCLUSIVE")
                self.assertIn("evaluation." + field + ".missing", result.reasons)

    def test_missing_dataset_rights_or_split_evidence_is_inconclusive(self):
        original = sample()
        for key in ("rights_ref", "partition_ref"):
            with self.subTest(key=key):
                result = inspect_training_candidate(replace(original, **{key: None}))
                self.assertEqual(result.status, "INCONCLUSIVE")
                self.assertIn("candidate." + key + ".missing", result.reasons)

    def test_malformed_reference_and_invalid_types_refuse(self):
        self.assertEqual(inspect_training_candidate(None).status, "REFUSED")
        original = sample()
        bad = (replace(original, generation=replace(original.generation, policy_ref=OwnerRef("", "broken"))),
               replace(original, generation=replace(original.generation, actor="third-party")),
               replace(original, evaluation=replace(original.evaluation, acceptance=True)),
               replace(original, method="invented"),
               replace(original, generation=replace(original.generation, token_ref="fake-digest")))
        for record in bad:
            with self.subTest(record=record):
                self.assertEqual(inspect_training_candidate(record).status, "REFUSED")

    def test_pure_inspector_never_reads_files_executes_or_contacts_network(self):
        with patch("builtins.open", side_effect=AssertionError("file")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("socket.socket", side_effect=AssertionError("network")):
            self.assertEqual(inspect_training_candidate(sample()).status, "STRUCTURALLY_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
