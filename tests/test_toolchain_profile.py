"""Source-only toolchain profile checks; no compiler/host effect."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ToolchainProfileTests(unittest.TestCase):
 def test_selection_is_not_falsely_an_installed_runtime(self):
  p=json.loads((ROOT/'docs/toolchain-profile.json').read_text())
  self.assertEqual(p['typescript_native'],'npm:typescript@7.0.2')
  self.assertEqual(p['compiler_api'],'npm:@typescript/typescript6@6.0.2')
  self.assertTrue(all(v is False for v in p['installed'].values()))
  self.assertFalse((ROOT/'package.json').exists())
  self.assertFalse((ROOT/'bun.lock').exists())
  d=(ROOT/'docs/typescript7-bun-tanstack-tsrs.md').read_text()
  for name in ('Noodle PR #122','medium-compiler PR #72','Soodles migrate-class PR #444','matching-revision','NOT_RUN'):
   self.assertIn(name,d)
if __name__=='__main__': unittest.main()
