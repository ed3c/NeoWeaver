"""A6.1 original readback relation tests; not native receipt authenticity."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from neoweaver.evidence import verify_owner_evidence, read_pinned_owner_evidence
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




def producer_receipt_payload(reference, readback="observed"):
    return {"ref": {"producer": reference.producer, "reference": reference.reference},
            "readback": readback}


class PinnedOwnerSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "original-owner"
        self.root.mkdir()
        self.candidate = sample()
        self.selected = {}
        for name, data in receipts_for(self.candidate).items():
            raw = (json.dumps(producer_receipt_payload(data["ref"]),
                              sort_keys=True) + "\n").encode()
            path = self.root / (name + ".json")
            path.write_bytes(raw)
            self.selected[name] = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}

    def verify(self, *, selection=None, candidate=None):
        return read_pinned_owner_evidence(candidate or self.candidate,
                                          self.selected if selection is None else selection,
                                          owner_root=self.root)

    def test_actual_read_from_host_selected_original_files_is_non_authorizing(self):
        result = self.verify()
        self.assertEqual(result.status, "SOURCE_BYTES_MATCH_DECLARATIONS")
        self.assertCountEqual(result.checked, self.selected)
        self.assertFalse(result.eligible_for_training)
        self.assertFalse(result.authorizes_landing)

    def test_modified_source_refuses_even_if_old_declaration_matched(self):
        (self.root / "reward.json").write_text('{"ref": {"producer": "attacker", "reference": "reward"}, "readback": "observed"}')
        result = self.verify()
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("reward.digest_mismatch", result.reasons)

    def test_new_self_asserted_readback_without_correct_reference_refuses(self):
        name = "rights"
        path = self.root / (name + ".json")
        raw = json.dumps(producer_receipt_payload(self.candidate.evaluation.reward_ref)).encode()
        path.write_bytes(raw)
        selection = dict(self.selected, rights={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()})
        result = self.verify(selection=selection)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("rights.ref_mismatch", result.reasons)

    def test_unknown_source_readback_does_not_become_verified(self):
        path = self.root / "verifier.json"
        raw = json.dumps(producer_receipt_payload(self.candidate.evaluation.verifier_ref, "unknown")).encode()
        path.write_bytes(raw)
        selection = dict(self.selected, verifier={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()})
        result = self.verify(selection=selection)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("verifier.not_observed", result.reasons)

    def test_missing_source_and_missing_selection_remain_unknown(self):
        (self.root / "oracle.json").unlink()
        selected = {k: v for k, v in self.selected.items() if k != "rights"}
        result = self.verify(selection=selected)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("rights.missing", result.reasons)
        self.assertIn("oracle.source_missing", result.reasons)

    def test_symlink_to_other_file_and_outside_owner_root_refuse(self):
        malicious = self.root / "fake.json"
        malicious.symlink_to(self.root / "rights.json")
        selected = dict(self.selected, rights={**self.selected["rights"], "path": str(malicious)})
        result = self.verify(selection=selected)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("rights.unreadable_source", result.reasons)
        selected["rights"] = {"path": str(self.root.parent / "untrusted.json"),
                              "sha256": self.selected["rights"]["sha256"]}
        result = self.verify(selection=selected)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("rights.outside_owner_root", result.reasons)

    def test_duplicate_receipt_file_cannot_prove_distinct_owner_slots(self):
        # The selected path is reused, regardless of digest equality.
        selected = dict(self.selected, partition=self.selected["rights"])
        result = self.verify(selection=selected)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("partition.reused_source_file", result.reasons)

    def test_invalid_json_and_duplicate_json_keys_refuse(self):
        path = self.root / "reward.json"
        for raw in (b'not json',
                    b'{"ref":{"producer":"x","producer":"y","reference":"z"},"readback":"observed"}',
                    b'{"ref":{},"readback":true}'):
            with self.subTest(raw=raw):
                path.write_bytes(raw)
                selected = dict(self.selected, reward={"path": str(path),
                                                       "sha256": hashlib.sha256(raw).hexdigest()})
                result = self.verify(selection=selected)
                self.assertEqual(result.status, "REFUSED")
                self.assertTrue(any("reward." in reason for reason in result.reasons))

    def test_nonfinite_payload_and_extra_fields_refuse(self):
        path = self.root / "rights.json"
        for raw in (b'{"ref":{},"readback":NaN}', b'{"ref":{},"readback":"observed","authorization":true}'):
            with self.subTest(raw=raw):
                path.write_bytes(raw)
                selected = dict(self.selected, rights={"path": str(path),
                                                       "sha256": hashlib.sha256(raw).hexdigest()})
                self.assertEqual(self.verify(selection=selected).status, "REFUSED")

    def test_oversized_source_is_not_ingested(self):
        path = self.root / "policy.json"
        raw = b"x" * (1024 * 1024 + 1)
        path.write_bytes(raw)
        selected = dict(self.selected, policy={"path": str(path),
                                               "sha256": hashlib.sha256(raw).hexdigest()})
        result = self.verify(selection=selected)
        self.assertIn("policy.source_too_large", result.reasons)

    def test_unexpected_slot_and_invalid_sha_refuse_without_training(self):
        selected = dict(self.selected, foreign=self.selected["rights"])
        self.assertEqual(self.verify(selection=selected).status, "REFUSED")
        selected = dict(self.selected, rights={**self.selected["rights"], "sha256": "guess"})
        result = self.verify(selection=selected)
        self.assertIn("rights.invalid_file_ref", result.reasons)
        self.assertFalse(result.eligible_for_training)

    def test_original_hard_refusal_stops_before_any_source_loading(self):
        candidate = replace(self.candidate, partition="held_out")
        result = self.verify(candidate=candidate)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(result.checked, ())

    def test_pinned_file_refs_do_not_mutate_or_run_provider_effects(self):
        from unittest.mock import patch
        with patch("subprocess.Popen", side_effect=AssertionError("spawn")), \
             patch("socket.socket", side_effect=AssertionError("network")):
            self.assertEqual(self.verify().status, "SOURCE_BYTES_MATCH_DECLARATIONS")


if __name__ == "__main__":
    unittest.main()
