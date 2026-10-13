"""Actual artifact consistency controls; not parser or native behavior tests."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts/check_compiled_contracts.py'


class CompiledContractsTests(unittest.TestCase):
    def run_check(self, root, code=0):
        result = subprocess.run([sys.executable, str(CHECK), '--root', str(root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout if code == 0 else result.stderr)

    def mutate(self, name, edit):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / 'docs/compiled', root / 'docs/compiled')
            path = root / 'docs/compiled' / name
            data = json.loads(path.read_text())
            edit(data)
            path.write_text(json.dumps(data))
            return self.run_check(root, 2)

    def test_current_artifact_retains_proof_ceiling(self):
        out = self.run_check(ROOT)
        self.assertEqual((out['requirements'], out['cards'], out['selected_cards']), (10, 44, 6))
        self.assertEqual(out['proof_ceiling'], 'DECLARED_ARTIFACT_CONSISTENCY_ONLY')
        self.assertEqual(out['source_semantics'], 'UNVERIFIED')
        self.assertEqual(out['parser_implementation'], 'NOT_RUN')
        self.assertEqual(out['native_pclass'], 'NOT_RUN')
        self.assertEqual(out['effects'], [])

    def test_parser_cannot_gain_replay(self):
        out = self.mutate('semantic-sidecars.json', lambda d: d['ScopeManifest']['local_contract'].__setitem__('executes_replay', True))
        self.assertEqual(out['error'], 'parser_effect_boundary_changed')

    def test_parent_requirement_cannot_disappear_from_continuation(self):
        out = self.mutate('semantic-sidecars.json', lambda d: d['Continuation']['original_requirement_ids'].pop())
        self.assertEqual(out['error'], 'parent_inventory_changed')

    def test_missing_native_training_gap_stays_visible(self):
        out = self.mutate('specification.json', lambda d: next(r for r in d['requirements'] if r['id'] == 'REQ-two-policies').pop('depends_on'))
        self.assertEqual(out['error'], 'missing_declared_gap_dependency:REQ-two-policies')

    def test_semantic_target_must_bind_to_the_actual_record(self):
        out = self.mutate('card-proposals.json', lambda d: d['cards'][7]['links'][0].__setitem__('target_topic', 'Absent target'))
        self.assertEqual(out['error'], 'unbound_semantic_target:SPEC-trainability-boundary')

    def test_parent_lifecycle_cannot_become_a_local_parser_exit(self):
        def select_deferred(d):
            entry = next(e for e in d['ScopeManifest']['card_applicability'] if e['card_id'] == 'SPEC-full-lifecycle-boundary')
            entry['selected'] = True
        out = self.mutate('semantic-sidecars.json', select_deferred)
        self.assertEqual(out['error'], 'selected_applicability_mismatch')

    def test_proposal_cannot_claim_native_consumption(self):
        out = self.mutate('semantic-sidecars.json', lambda d: d['PromptDelta'].__setitem__('native_consumption', 'PASS'))
        self.assertEqual(out['error'], 'unobserved_native_consumption_claim')

    def test_raw_duplicate_keys_refuse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / 'docs/compiled', root / 'docs/compiled')
            (root / 'docs/compiled/specification.json').write_text('{"cards":[],"cards":[]}')
            self.assertEqual(self.run_check(root, 2)['error'], 'duplicate_json_key:cards')


if __name__ == '__main__':
    unittest.main()
