"""Exercise real subprocess CLI and original pinned transport using a synthetic Owner."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from test_product_goal import ProductFixture, ROOT, ref

CLI = [sys.executable, '-B', str(ROOT / 'scripts/neoweaver.py')]
OWNER = '''import hashlib, json, pathlib, sys, time
root = pathlib.Path(__file__).parent
config = json.loads((root / "owner-config.json").read_text())
if sys.argv[1] == "manager-request":
    tool = "soodles_" + sys.argv[2]
    arguments = json.load(sys.stdin)
else:
    tool = "soodles_loop_enter"
    arguments = {"request_file": sys.argv[sys.argv.index("--request-file") + 1]}
request = pathlib.Path(arguments["request_file"])
assert request.read_bytes() == bytes.fromhex(config["request_hex"])
state = root / "owner-state.json"
result = json.loads(state.read_text()) if state.exists() else config["initial"]
if tool != "soodles_loop_inspect":
    effects = root / "effects.json"
    history = json.loads(effects.read_text()) if effects.exists() else []
    history.append({"tool":tool,"arguments":arguments})
    effects.write_text(json.dumps(history))
    result = config["after"][min(len(history)-1, len(config["after"])-1)]
    state.write_text(json.dumps(result))
    if config.get("delay"):
        time.sleep(config["delay"])
print(json.dumps(result))
'''


class TransportFixture(ProductFixture):
    def setUp(self):
        super().setUp()
        self.owner = self.base / 'owner.py'
        self.owner.write_text(OWNER)
        self.config = {'request_hex': self.request_bytes.hex(), 'initial': self.result,
                       'after': [self.integrated()]}
        self.save_config()
        self.selection['tasks']['A']['carrier'] = {
            'python': ref(Path(sys.executable).resolve()), 'entrypoint': ref(self.owner),
            'sources': [ref(self.owner)], 'source_commit': 'synthetic-test-only',
            'environment': {}, 'timeout_s': 3, 'require_existing_instance': 'synthetic-test-only'}

    def save_config(self):
        (self.base / 'owner-config.json').write_text(json.dumps(self.config))

    def run_cli(self, resource, verb, arguments, *flags):
        run = subprocess.run(CLI + [resource, verb, '--stdin', *flags], input=json.dumps(arguments),
                             text=True, capture_output=True, timeout=20)
        payload = json.loads(run.stdout or run.stderr)
        return run, payload

    def effects(self):
        path = self.base / 'effects.json'
        try:
            return json.loads(path.read_text()) if path.exists() else []
        except json.JSONDecodeError:
            return []

    def continuation(self, **extra):
        return {'selection': self.selection, 'task': 'A', 'capture': str(self.base / 'continue'), **extra}


class ProductCLITests(TransportFixture):
    def test_mechanical_chain_reaches_original_acceptance_without_new_ledger(self):
        middle = deepcopy(self.result)
        middle['next'] = {'tool': 'soodles_loop_recover_completion',
                          'arguments': {'request_file': self.request['path']}}
        final = self.integrated()
        final['next'] = None
        self.config['after'] = [middle, final]
        self.save_config()
        run, output = self.run_cli('task', 'continue', self.continuation())
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(output['trace']), 2)
        self.assertEqual(output['boundary'], 'original_owner_boundary')
        self.assertEqual(len(output['product']['locally_completed']), 1)
        self.assertEqual([r['tool'] for r in self.effects()],
                         ['soodles_loop_enter', 'soodles_loop_recover_completion'])
        self.assertEqual(self.request_path.read_bytes(), self.request_bytes)
        self.assertEqual(output['product']['whole_goal'], 'OPEN')

    def test_dry_run_and_resend_do_not_duplicate_effect(self):
        arguments = self.continuation()
        run, output = self.run_cli('task', 'continue', arguments, '--dry-run')
        self.assertEqual(output['status'], 'dry_run')
        self.assertEqual(self.effects(), [])
        self.assertFalse(Path(arguments['capture']).exists())
        self.run_cli('task', 'continue', arguments)
        run, output = self.run_cli('task', 'continue', arguments)
        self.assertEqual(output['status'], 'unknown')
        self.assertEqual(output['problem'], 'capture_exists_read_original_owner')
        self.assertEqual(len(self.effects()), 1)

    def test_parallel_same_capture_reserves_once(self):
        arguments = json.dumps(self.continuation())
        processes = [subprocess.Popen(CLI + ['task', 'continue', '--stdin'], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        for process in processes:
            process.stdin.write(arguments)
            process.stdin.close()
            process.stdin = None
        outputs = [json.loads(''.join(process.communicate(timeout=20))) for process in processes]
        self.assertEqual(sum(o['status'] == 'unknown' for o in outputs), 1)
        self.assertEqual(len(self.effects()), 1)

    def test_timeout_after_effect_is_unknown_then_refresh_only_reads(self):
        self.config['delay'] = 2
        self.save_config()
        self.selection['tasks']['A']['carrier']['timeout_s'] = 0.5
        run, output = self.run_cli('task', 'continue', self.continuation())
        self.assertEqual(output['status'], 'unknown')
        self.assertEqual(len(self.effects()), 1)
        run, current = self.run_cli('goal', 'refresh', {'selection': self.selection,
                                                      'capture': str(self.base / 'refresh')})
        self.assertEqual(len(current['locally_completed']), 1)
        self.assertEqual(len(self.effects()), 1)
        self.assertEqual(self.request_path.read_bytes(), self.request_bytes)

    def test_review_is_named_and_never_automatically_approved(self):
        review = deepcopy(self.result)
        review['review_input'] = {'kind': 'session_judgment', 'tool': 'soodles_loop_candidate_review',
                                  'arguments': {'request_file': self.request['path'], 'candidate': 'synthetic'}}
        self.config['initial'] = review
        self.save_config()
        self.selection['tasks']['A']['readback'] = self.save_result(review)
        run, output = self.run_cli('task', 'continue', self.continuation())
        self.assertEqual(output['status'], 'needs_review')
        self.assertEqual(self.effects(), [])
        arguments = self.continuation(review={'decision': 'request-changes', 'feedback': 'synthetic negative'})
        arguments['capture'] = str(self.base / 'review')
        run, output = self.run_cli('task', 'continue', arguments)
        self.assertEqual(self.effects()[0]['arguments']['decision'], 'request-changes')

    def test_stale_continuation_refused_before_effect(self):
        self.config['initial'] = {**self.result, 'next': {'kind': 'new_boundary'}}
        self.save_config()
        run, output = self.run_cli('task', 'continue', self.continuation())
        self.assertEqual(run.returncode, 2)
        self.assertIn('original_continuation_changed', output['problem'])
        self.assertEqual(self.effects(), [])

    def test_strict_json_flags_and_file_input(self):
        for raw in ('{"selection":{},"selection":{}}', '{"facts":NaN}', '[]'):
            run = subprocess.run(CLI + ['goal', 'reconcile', '--stdin'], input=raw,
                                 text=True, capture_output=True, timeout=5)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stderr)['status'], 'refused')
        run = subprocess.run(CLI + ['goal', 'reconcile'], capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 2)
        self.assertIn('Example:', json.loads(run.stderr)['problem'])
        path = self.base / 'arguments.json'
        path.write_text(json.dumps({'selection': self.selection}))
        run = subprocess.run(CLI + ['goal', 'reconcile', '--input', str(path)], capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['whole_goal'], 'OPEN')

    def test_supplied_a6_facts_use_existing_screen(self):
        facts = {'actor': 'frozen_codex', 'method': 'sft', 'partition': 'train', 'rights': 'unknown',
                 'acceptance': 'pass', 'protected_regressions': 'pass', 'effect_status': 'unknown',
                 'lineage': 'matched', 'token_provenance': 'missing', 'replay': 'observed',
                 'verifier': 'independent', 'reward': 'observed'}
        run, output = self.run_cli('training', 'inspect', {'facts': facts})
        self.assertEqual(output['status'], 'BLOCKED')
        self.assertFalse(output['eligible_for_training'])
        self.assertIn('frozen_codex_not_trainable', output['reasons'])


if __name__ == '__main__':
    unittest.main()
