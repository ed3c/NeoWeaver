"""Structural checks for the inert proposed episode visualization schema."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "episode-view-v1.schema.json"

class EpisodeViewSchemaTests(unittest.TestCase):
    def test_readonly_contract_and_explicit_unknown(self):
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        for name in ("execute", "train", "publish", "accept"):
            self.assertIs(schema["properties"]["permissions"]["properties"][name]["const"], False)
        self.assertIn("UNKNOWN", schema["properties"]["display"]["properties"]["status"]["enum"])
        self.assertIn("held_out", schema["properties"]["learning"]["properties"]["partition"]["enum"])

if __name__ == "__main__":
    unittest.main()
