"""A6.1 original readback relation tests; not native receipt authenticity."""
from dataclasses import replace
import unittest

from neoweaver.evidence import verify_owner_evidence
from neoweaver.learning import inspect_training_candidate
from test_learning import sample


def receipts_for(candidate):
    g, e = candidate.generation, candidate.evaluation
    refs = {
        "rights": candidate.rights_ref, "partition": candidate.partition_ref,
        "policy": g.policy_ref, "observation": g.observation_ref,
        "action": g.action_ref, "generation": g.generation_ref,
        "rollout": e.rollout_ref, "replay": e.replay_ref,
        "verifier": e.verifier_ref, "oracle": e.oracle_ref,
        "reward": e.reward_ref, "tokens": g.token_ref,
    }
    return {name: {"ref": ref, "readback": "observed"} for name, ref in refs.items() if ref is not None}


class EvidenceReadbackTests(unittest.TestCase):
    def test_matching_receipts_never_grant_training(self):
        candidate = sample()
        result = verify_owner_evidence(candidate, receipts_for(candidate))
        self.assertEqual(result.status, "RECEIPTS_MATCH_DECLARATIONS")
        self.assertFalse(result.eligible_for_training)
        self.assertFalse(result.authorizes_landing)

    def test_missing_and_unobserved_preserve_unknown(self):
        candidate = sample()
        receipts = receipts_for(candidate)
        del receipts["oracle"]
        receipts["reward"]["readback"] = "unknown"
        result = verify_owner_evidence(candidate, receipts)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("oracle.missing", result.reasons)
        self.assertIn("reward.not_observed", result.reasons)

    def test_foreign_ref_refuses(self):
        candidate = sample()
        receipts = receipts_for(candidate)
        receipts["rights"] = receipts["oracle"]
        result = verify_owner_evidence(candidate, receipts)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("rights.ref_mismatch", result.reasons)

    def test_hard_gate_precedes_receipt_readback(self):
        candidate = replace(sample(), partition="held_out")
        self.assertEqual(verify_owner_evidence(candidate, {}).status, "BLOCKED")

    def test_missing_token_cannot_be_invented(self):
        candidate = sample(method="policy_gradient")
        receipts = receipts_for(candidate)
        del receipts["tokens"]
        self.assertEqual(verify_owner_evidence(candidate, receipts).status, "INCONCLUSIVE")

    def test_invalid_receipt_type_refuses(self):
        candidate = sample()
        receipts = receipts_for(candidate)
        receipts["replay"] = "fake"
        self.assertEqual(verify_owner_evidence(candidate, receipts).status, "REFUSED")


if __name__ == "__main__":
    unittest.main()
