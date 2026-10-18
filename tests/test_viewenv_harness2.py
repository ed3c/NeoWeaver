import json
import unittest

from neoweaver.patches import KIND, DiagnosticRefusal
from neoweaver.viewenv_harness2 import (
    Harness2BridgeRefusal, propose_bounded_harness, inspect_original_harness_probe
)
from test_viewenv import fixture


class Harness2BridgeTests(unittest.TestCase):
    def test_original_parser_is_only_mutation_gate(self):
        spec,raw=fixture()
        proposed=propose_bounded_harness(raw,spec.fixed_inputs)
        self.assertEqual("skill_instruction",proposed.surface)
        self.assertEqual(1,proposed.k)
        self.assertFalse(proposed.executes_native_probe)
        self.assertFalse(proposed.authorizes_landing)

    def test_protected_mutation_remains_original_refusal(self):
        spec,raw=fixture()
        doc=json.loads(raw)
        doc["changes"][0]["target_ref"]={"producer":"owner","reference":"oracle"}
        result=propose_bounded_harness(json.dumps(doc).encode(),spec.fixed_inputs)
        self.assertIsInstance(result,DiagnosticRefusal)
        self.assertEqual("protected_target",result.condition)

    def test_fake_completed_probe_cannot_make_reward(self):
        with self.assertRaises(Harness2BridgeRefusal):
            inspect_original_harness_probe({"pair":{"status":"STRUCTURALLY_COMPARABLE"}})


if __name__=="__main__":
    unittest.main()
