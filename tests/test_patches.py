"""Public parser controls: data acceptance/refusal, never replay or native effects."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from neoweaver.patches import Change, DiagnosticRefusal, OwnerRef, ParsedProposal, parse_proposal


ROOT = Path(__file__).resolve().parents[1]


def ref(name, producer="owner"):
    return {"producer": producer, "reference": name}


def inputs(surface="skill_instruction"):
    return {
        "snapshot_ref": ref("snapshot-1"),
        "failure_ref": ref("failure-1"),
        "allowlist_ref": ref("allowlist-1"),
        "acceptance_ref": ref("acceptance-1"),
        "causal_target_ref": ref("target-1"),
        "allowlist": [{"surface": surface, "target_ref": ref("target-1"),
                       "expected_source_ref": ref("source-1")}],
        "protected_target_refs": [ref("oracle-1"), ref("evaluator-1")],
    }


def proposal(surface="skill_instruction"):
    return {"kind": "neoweaver/patch-proposal/v1", "snapshot_ref": ref("snapshot-1"),
            "failure_ref": ref("failure-1"), "allowlist_ref": ref("allowlist-1"),
            "acceptance_ref": ref("acceptance-1"), "surface": surface,
            "changes": [{"target_ref": ref("target-1"), "expected_source_ref": ref("source-1"),
                         "replacement": "Only parse the selected proposal.\n"}]}


def encode(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


class PatchParserTests(unittest.TestCase):
    def refused(self, raw, fixed, condition, path=None):
        result = parse_proposal(raw, fixed)
        self.assertIsInstance(result, DiagnosticRefusal)
        self.assertEqual(result.condition, condition)
        self.assertEqual(result.raw, raw if type(raw) is bytes else None)
        if path is not None:
            self.assertEqual(result.path, path)
        return result

    def test_all_three_surfaces_accept_literal_data(self):
        for surface in ("skill_instruction", "context_policy", "mcp_wrapper"):
            with self.subTest(surface=surface):
                raw = encode(proposal(surface))
                result = parse_proposal(raw, inputs(surface))
                self.assertIsInstance(result, ParsedProposal)
                self.assertEqual(result.raw, raw)
                self.assertEqual(result.kind, "neoweaver/patch-proposal/v1")
                self.assertEqual(result.surface, surface)
                self.assertEqual(result.snapshot_ref, OwnerRef("owner", "snapshot-1"))
                self.assertEqual(result.failure_ref, OwnerRef("owner", "failure-1"))
                self.assertEqual(result.allowlist_ref, OwnerRef("owner", "allowlist-1"))
                self.assertEqual(result.acceptance_ref, OwnerRef("owner", "acceptance-1"))
                self.assertEqual(result.changes, (Change(OwnerRef("owner", "target-1"),
                                                       OwnerRef("owner", "source-1"),
                                                       "Only parse the selected proposal.\n"),))

    def test_results_detach_fixed_owner_data_and_are_immutable(self):
        fixed = inputs()
        result = parse_proposal(encode(proposal()), fixed)
        fixed["allowlist"][0]["expected_source_ref"]["reference"] = "changed"
        fixed["protected_target_refs"].clear()
        self.assertEqual(result.fixed_inputs.allowlist[0].expected_source_ref, OwnerRef("owner", "source-1"))
        self.assertEqual(result.fixed_inputs.protected_target_refs,
                         (OwnerRef("owner", "oracle-1"), OwnerRef("owner", "evaluator-1")))
        with self.assertRaises(FrozenInstanceError):
            result.changes[0].replacement = "changed"
        with self.assertRaises(FrozenInstanceError):
            result.fixed_inputs.acceptance_ref.reference = "changed"
        with self.assertRaises(FrozenInstanceError):
            result.raw = b"changed"

    def test_same_raw_and_fixed_boundary_produce_equal_data(self):
        raw = encode(proposal())
        self.assertEqual(parse_proposal(raw, inputs()), parse_proposal(raw, inputs()))
        bad = raw.replace(b'"source-1"', b'"stale"')
        self.assertEqual(parse_proposal(bad, inputs()), parse_proposal(bad, inputs()))

    def test_duplicate_keys_at_top_and_nested_levels_refuse(self):
        for raw, key in ((b'{"kind":1,"kind":2}', "kind"),
                         (b'{"snapshot_ref":{"producer":"owner","producer":"other"}}', "producer"),
                         (b'{"changes":[{"replacement":"a","replacement":"b"}]}', "replacement")):
            with self.subTest(key=key):
                self.refused(raw, inputs(), "duplicate_json_key", key)

    def test_invalid_utf8_and_malformed_json_refuse(self):
        self.refused(b"\xff", inputs(), "invalid_utf8", "$raw")
        for raw in (b"", b"{", b"{} trailing", b"{}{}", b'{"a":01}', b"\xef\xbb\xbf{}"):
            with self.subTest(raw=raw):
                self.refused(raw, inputs(), "malformed_json", "$raw")

    def test_nonfinite_numbers_refuse_even_in_an_extra_field(self):
        for number in ("NaN", "Infinity", "-Infinity", "1e999"):
            raw = encode(proposal())[:-1] + (',"hidden":' + number + '}').encode()
            self.refused(raw, inputs(), "nonfinite_json_number", "$raw")

    def test_raw_type_and_top_level_type_refuse(self):
        for raw in (None, "{}", bytearray(b"{}")):
            self.refused(raw, inputs(), "invalid_raw_type", "$raw")
        for raw in (b"null", b"[]", b"1", b'"text"'):
            self.refused(raw, inputs(), "invalid_type", "proposal")

    def test_wrong_proposal_field_types_refuse(self):
        cases = (("snapshot_ref", [], "proposal.snapshot_ref"),
                 ("surface", True, "proposal.surface"),
                 ("changes", {}, "proposal.changes"))
        for key, value, path in cases:
            data = proposal()
            data[key] = value
            self.refused(encode(data), inputs(), "invalid_type", path)
        data = proposal()
        data["changes"][0]["replacement"] = False
        self.refused(encode(data), inputs(), "invalid_type", "proposal.changes[0].replacement")

    def test_missing_proposal_fields_refuse(self):
        for key in proposal():
            data = proposal()
            del data[key]
            self.refused(encode(data), inputs(), "missing_field", "proposal." + key)

    def test_nested_missing_fields_and_nonobject_change_refuse(self):
        for key in ("target_ref", "expected_source_ref", "replacement"):
            data = proposal()
            del data["changes"][0][key]
            self.refused(encode(data), inputs(), "missing_field", "proposal.changes[0]." + key)
        data = proposal()
        del data["failure_ref"]["producer"]
        self.refused(encode(data), inputs(), "missing_field", "proposal.failure_ref.producer")
        data = proposal()
        data["changes"] = [None]
        self.refused(encode(data), inputs(), "invalid_type", "proposal.changes[0]")

    def test_unknown_kind_and_surface_refuse(self):
        data = proposal()
        data["kind"] = "other/v1"
        self.refused(encode(data), inputs(), "unsupported_kind", "proposal.kind")
        data = proposal()
        data["surface"] = "native_transfer"
        self.refused(encode(data), inputs(), "unsupported_surface", "proposal.surface")

    def test_empty_replacement_changes_and_owner_ref_refuse(self):
        data = proposal()
        data["changes"] = []
        self.refused(encode(data), inputs(), "empty_changes", "proposal.changes")
        data = proposal()
        data["changes"][0]["replacement"] = ""
        self.refused(encode(data), inputs(), "empty_string", "proposal.changes[0].replacement")
        data = proposal()
        data["failure_ref"]["reference"] = ""
        self.refused(encode(data), inputs(), "empty_string", "proposal.failure_ref.reference")

    def test_lone_surrogate_refuses(self):
        raw = encode(proposal()).replace(b"Only parse the selected proposal.", b"\\ud800")
        self.refused(raw, inputs(), "invalid_unicode_string", "proposal.changes[0].replacement")

    def test_fixed_references_match_both_opaque_fields_exactly(self):
        for key in ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref"):
            for field in ("producer", "reference"):
                data = proposal()
                data[key][field] += "-other"
                self.refused(encode(data), inputs(), "fixed_reference_mismatch", "proposal." + key)

    def test_stale_source_refuses_both_producer_and_reference_mismatch(self):
        for field in ("producer", "reference"):
            data = proposal()
            data["changes"][0]["expected_source_ref"][field] += "-stale"
            self.refused(encode(data), inputs(), "stale_expected_source",
                         "proposal.changes[0].expected_source_ref")

    def test_unlisted_target_and_wrong_surface_allowlist_refuse(self):
        data = proposal()
        data["changes"][0]["target_ref"] = ref("target-2")
        self.refused(encode(data), inputs(), "target_outside_allowlist")
        self.refused(encode(proposal("context_policy")), inputs(), "target_outside_allowlist")

    def test_allowed_target_must_equal_fixed_failure_causal_target(self):
        fixed = inputs()
        fixed["causal_target_ref"] = ref("different-causal-target")
        self.refused(encode(proposal()), fixed, "causal_target_mismatch")

    def test_protected_oracle_evaluator_and_acceptance_override_allowlist(self):
        for name in ("oracle-1", "evaluator-1", "acceptance-1"):
            fixed = inputs()
            fixed["causal_target_ref"] = ref(name)
            fixed["allowlist"][0]["target_ref"] = ref(name)
            data = proposal()
            data["changes"][0]["target_ref"] = ref(name)
            self.refused(encode(data), fixed, "protected_target")

    def test_multiple_causal_targets_refuse(self):
        data = proposal()
        second = deepcopy(data["changes"][0])
        second["target_ref"] = ref("target-2")
        data["changes"].append(second)
        self.refused(encode(data), inputs(), "multiple_causal_targets", "proposal.changes")

    def test_multiple_whole_replacements_of_same_target_refuse_without_order_guess(self):
        for replacement in ("second replacement", "Only parse the selected proposal.\n"):
            data = proposal()
            second = deepcopy(data["changes"][0])
            second["replacement"] = replacement
            data["changes"].append(second)
            self.refused(encode(data), inputs(), "ambiguous_replacement_order", "proposal.changes")

    def test_extra_effect_credential_and_unknown_fields_refuse_at_every_level(self):
        for container, path in (("proposal", "proposal"), ("change", "proposal.changes[0]"),
                                ("ref", "proposal.failure_ref")):
            for key in ("credential", "effects", "argv", "unknown"):
                data = proposal()
                target = data if container == "proposal" else data["changes"][0] if container == "change" else data["failure_ref"]
                target[key] = "do something"
                self.refused(encode(data), inputs(), "extra_field", path + "." + key)

    def test_missing_fixed_input_refuses_before_parsing_proposal(self):
        for key in inputs():
            fixed = inputs()
            del fixed[key]
            result = self.refused(b"not JSON", fixed, "missing_fixed_input", "fixed_inputs." + key)
            self.assertIsNone(result.fixed_inputs)

    def test_invalid_and_empty_fixed_input_refuse(self):
        self.refused(encode(proposal()), None, "invalid_fixed_input_type", "fixed_inputs")
        for key, value, condition, path in (
            ("snapshot_ref", None, "invalid_fixed_input_type", "fixed_inputs.snapshot_ref"),
            ("allowlist", [], "empty_fixed_input", "fixed_inputs.allowlist"),
            ("protected_target_refs", None, "invalid_fixed_input_type", "fixed_inputs.protected_target_refs"),
        ):
            fixed = inputs()
            fixed[key] = value
            self.refused(encode(proposal()), fixed, condition, path)
        fixed = inputs()
        fixed["snapshot_ref"]["reference"] = ""
        self.refused(encode(proposal()), fixed, "empty_fixed_input", "fixed_inputs.snapshot_ref.reference")

    def test_ambiguous_allowlist_and_extra_fixed_fields_refuse(self):
        fixed = inputs()
        fixed["allowlist"].append(deepcopy(fixed["allowlist"][0]))
        self.refused(encode(proposal()), fixed, "ambiguous_allowlist", "fixed_inputs.allowlist[1]")
        fixed = inputs()
        fixed["credentials"] = "not required"
        self.refused(encode(proposal()), fixed, "extra_fixed_input", "fixed_inputs.credentials")

    def test_nested_fixed_input_fields_and_types_refuse(self):
        fixed = inputs()
        del fixed["allowlist"][0]["expected_source_ref"]
        self.refused(encode(proposal()), fixed, "missing_fixed_input",
                     "fixed_inputs.allowlist[0].expected_source_ref")
        fixed = inputs()
        fixed["allowlist"][0]["effect"] = "write"
        self.refused(encode(proposal()), fixed, "extra_fixed_input", "fixed_inputs.allowlist[0].effect")
        fixed = inputs()
        fixed["protected_target_refs"][0]["reference"] = False
        self.refused(encode(proposal()), fixed, "invalid_fixed_input_type",
                     "fixed_inputs.protected_target_refs[0].reference")

    def test_refusal_preserves_valid_fixed_refs_and_is_immutable(self):
        result = self.refused(b"{", inputs(), "malformed_json")
        self.assertEqual(result.fixed_inputs.acceptance_ref, OwnerRef("owner", "acceptance-1"))
        with self.assertRaises(FrozenInstanceError):
            result.condition = "PASS"

    def test_opaque_path_like_refs_and_replacement_are_not_read_or_executed(self):
        fixed = inputs()
        opaque = ref("../../private/nonexistent-file", "https://unknown.invalid/owner")
        fixed["causal_target_ref"] = opaque
        fixed["allowlist"][0]["target_ref"] = opaque
        fixed["protected_target_refs"] = []
        data = proposal()
        data["changes"][0]["target_ref"] = opaque
        data["changes"][0]["replacement"] = "__import__('os').system('should never execute')"
        with patch("builtins.open", side_effect=AssertionError("file I/O")), \
             patch("os.system", side_effect=AssertionError("effect")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("socket.socket", side_effect=AssertionError("network")):
            result = parse_proposal(encode(data), fixed)
        self.assertIsInstance(result, ParsedProposal)
        self.assertEqual(result.changes[0].target_ref,
                         OwnerRef("https://unknown.invalid/owner", "../../private/nonexistent-file"))
        self.assertEqual(result.changes[0].replacement, "__import__('os').system('should never execute')")

    def test_public_shape_matches_pinned_proposed_schema(self):
        schema = json.loads((ROOT / "contracts/proposals/patch-proposal.schema.json").read_text())
        self.assertEqual(schema["type"], "object")
        self.assertEqual(set(schema["required"]),
                         {"kind", "snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref", "surface", "changes"})
        self.assertEqual(set(schema["properties"]), set(schema["required"]))
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(schema["properties"]["kind"]["const"], "neoweaver/patch-proposal/v1")
        self.assertEqual(schema["properties"]["surface"]["enum"],
                         ["skill_instruction", "context_policy", "mcp_wrapper"])
        self.assertEqual(schema["properties"]["changes"]["minItems"], 1)
        self.assertEqual(schema["properties"]["changes"]["type"], "array")
        for key in ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref"):
            self.assertEqual(schema["properties"][key], {"$ref": "#/$defs/ownerRef"})
        change = schema["properties"]["changes"]["items"]
        self.assertEqual(change["type"], "object")
        self.assertEqual(set(change["required"]), {"target_ref", "expected_source_ref", "replacement"})
        self.assertEqual(set(change["properties"]), set(change["required"]))
        self.assertIs(change["additionalProperties"], False)
        self.assertEqual(change["properties"]["replacement"], {"type": "string", "minLength": 1})
        for key in ("target_ref", "expected_source_ref"):
            self.assertEqual(change["properties"][key], {"$ref": "#/$defs/ownerRef"})
        owner_ref = schema["$defs"]["ownerRef"]
        self.assertEqual(owner_ref["type"], "object")
        self.assertEqual(set(owner_ref["required"]), {"producer", "reference"})
        self.assertEqual(owner_ref["properties"], {"producer": {"type": "string", "minLength": 1},
                                                  "reference": {"type": "string", "minLength": 1}})
        self.assertIs(owner_ref["additionalProperties"], False)
        self.assertIsInstance(parse_proposal(encode(proposal()), inputs()), ParsedProposal)


if __name__ == "__main__":
    unittest.main()
