"""Original-owner seam controls. Fake carriers do not establish Native delivery."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from neoweaver.task_adapter import PinnedLoopCLI, TaskAdapter, TransportUnknown


def reference(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class Carrier:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def call(self, tool, arguments, capture):
        self.calls.append((tool, deepcopy(arguments)))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        capture.mkdir()
        path = capture / 'stdout.json'
        path.write_text(json.dumps(response))
        return deepcopy(response), reference(path)


class TaskAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        request = self.root / 'request.json'
        request.write_text(json.dumps({'repository': str(self.repo)}))
        self.request = reference(request)
        self.result = {'owner': 'soodles.loop', 'request': self.request, 'status': 'running',
                       'inner': {}, 'next': {'tool': 'soodles_loop_inspect',
                                            'arguments': {'request_file': str(request)}}}

    def adapter(self, responses):
        self.carrier = Carrier(responses)
        return TaskAdapter(self.request, self.carrier)

    def reviewed_result(self):
        result = deepcopy(self.result)
        result['review_input'] = {
            'tool': 'soodles_loop_candidate_review', 'kind': 'session_judgment',
            'arguments': {'request_file': self.request['path'],
                          'candidate': {'path': 'original-candidate', 'sha256': 'original-digest'}},
            'required': ['decision', 'feedback']}
        return result

    def test_completed_writer_is_not_accepted(self):
        result = deepcopy(self.result)
        result['status'] = 'completed'
        adapter = self.adapter([result])
        state = adapter.inspect(self.root / 'read')
        self.assertEqual(state.status, 'waiting')
        self.assertEqual(state.owner_acceptance, 'UNKNOWN')
        self.assertIsNone(state.commit)
        self.assertIsNone(state.cost_usd)
        self.assertFalse(state.authorizes_landing)

    def test_malformed_owner_response_is_unknown_without_a_continuation(self):
        for index, value in enumerate(([], '', 0, False, ['invalid original response'])):
            for field in ('inner', 'review_progress', 'acceptance_report', 'next', 'review_input'):
                with self.subTest(field=field, value=value):
                    result = deepcopy(self.result)
                    if field in ('review_progress', 'acceptance_report'):
                        result['inner'][field] = value
                    else:
                        result[field] = value
                    adapter = self.adapter([result])
                    state = adapter.inspect(self.root / ('read-' + field + str(index)))
                    self.assertEqual(state.status, 'unknown')
                    self.assertIsNone(state.action)
                    self.assertIn('invalid_original_task_readback', state.result['problem'])

    def test_malformed_continuation_arguments_do_not_reach_execution(self):
        result = deepcopy(self.result)
        result['next'] = {'tool': 'soodles_loop_enter', 'arguments': []}
        adapter = self.adapter([result, result])
        previous = adapter.inspect(self.root / 'first')
        state = adapter.advance(previous, self.root / 'second')
        self.assertEqual(state.status, 'unknown')
        self.assertIsNone(state.action)
        self.assertEqual([call[0] for call in self.carrier.calls], ['soodles_loop_inspect'] * 2)

    def test_semantic_review_has_no_automatic_approval(self):
        result = self.reviewed_result()
        adapter = self.adapter([result, result])
        previous = adapter.inspect(self.root / 'first')
        state = adapter.advance(previous, self.root / 'second')
        self.assertEqual(state.status, 'needs_review')
        self.assertEqual([call[0] for call in self.carrier.calls], ['soodles_loop_inspect'] * 2)

    def test_request_changes_is_forwarded_once_to_original_candidate(self):
        result = self.reviewed_result()
        adapter = self.adapter([result, result, self.result])
        previous = adapter.inspect(self.root / 'first')
        review = {'decision': 'request-changes', 'feedback': 'Independent control failed.'}
        adapter.advance(previous, self.root / 'second', review=review)
        tool, arguments = self.carrier.calls[-1]
        self.assertEqual(tool, 'soodles_loop_candidate_review')
        self.assertEqual(arguments, {**result['review_input']['arguments'], **review})
        self.assertEqual(len(self.carrier.calls), 3)

    def test_changed_candidate_cannot_reuse_previous_review(self):
        previous_result = self.reviewed_result()
        changed = deepcopy(previous_result)
        changed['review_input']['arguments']['candidate']['sha256'] = 'new-original-digest'
        adapter = self.adapter([previous_result, changed])
        previous = adapter.inspect(self.root / 'first')
        with self.assertRaisesRegex(ValueError, 'original_continuation_changed'):
            adapter.advance(previous, self.root / 'second', review={'decision': 'approve'})
        self.assertEqual(len(self.carrier.calls), 2)

    def test_unknown_transport_only_reads_on_next_advance(self):
        adapter = self.adapter([TransportUnknown('lost original response'), self.result])
        previous = adapter.inspect(self.root / 'first')
        self.assertEqual(previous.status, 'unknown')
        state = adapter.advance(previous, self.root / 'second')
        self.assertEqual(state.status, 'waiting')
        self.assertEqual([call[0] for call in self.carrier.calls], ['soodles_loop_inspect'] * 2)

    def test_integrated_acceptance_remains_a_separate_owner_observation(self):
        record = self.root / 'original-acceptance.json'
        record.write_text(json.dumps({'head': 'a' * 40}))
        result = deepcopy(self.result)
        result['inner'] = {'review_progress': {'status': 'locally_integrated'},
                           'acceptance_report': {'status': 'PASS', 'scope': 'integrated',
                                                 'record': reference(record)}}
        adapter = self.adapter([result])
        state = adapter.inspect(self.root / 'read')
        self.assertEqual(state.status, 'integrated')
        self.assertEqual(state.owner_acceptance, 'PASS')
        self.assertEqual(state.commit, 'a' * 40)
        self.assertFalse(state.authorizes_landing)

    def test_integrated_review_barrier_still_requires_session_input(self):
        result = deepcopy(self.result)
        result['inner'] = {'review_progress': {'status': 'locally_integrated'}}
        result['next'] = {'tool': 'soodles_loop_candidate_continue', 'kind': 'session_judgment',
                          'arguments': {'request_file': self.request['path'],
                                        'candidate': {'path': 'original', 'sha256': 'original'},
                                        'acceptance_review': {'scope': 'integrated', 'conditions': []}}}
        adapter = self.adapter([result, result, self.result])
        state = adapter.inspect(self.root / 'first')
        self.assertEqual(state.status, 'needs_review')
        review = {'acceptance_review': {'scope': 'integrated', 'conditions': []}}
        adapter.advance(state, self.root / 'second', review=review)
        self.assertEqual(self.carrier.calls[-1][0], 'soodles_loop_candidate_continue')

    def test_foreign_request_and_source_drift_cannot_advance(self):
        result = deepcopy(self.result)
        result['next']['arguments']['request_file'] = str(self.root / 'other-request')
        adapter = self.adapter([result, result])
        previous = adapter.inspect(self.root / 'first')
        with self.assertRaisesRegex(ValueError, 'foreign_continuation_request'):
            adapter.advance(previous, self.root / 'second')
        Path(self.request['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source_changed'):
            adapter.inspect(self.root / 'third')
        self.assertEqual(len(self.carrier.calls), 2)

    def test_arbitrary_shell_continuation_is_never_executed(self):
        result = deepcopy(self.result)
        result['next'] = {'tool': 'shell', 'argv': ['untrusted-command']}
        adapter = self.adapter([result, result])
        previous = adapter.inspect(self.root / 'first')
        adapter.advance(previous, self.root / 'second')
        self.assertEqual([call[0] for call in self.carrier.calls], ['soodles_loop_inspect'] * 2)

    def test_repository_cannot_be_used_for_transport_captures(self):
        adapter = self.adapter([])
        with self.assertRaisesRegex(ValueError, 'capture_overlaps_repository'):
            adapter.inspect(self.repo / 'capture')
        self.assertEqual(self.carrier.calls, [])

    def test_real_transport_uses_named_cli_and_checks_selected_sources(self):
        entrypoint = self.root / 'fixture-cli.py'
        entrypoint.write_text('import json,sys\nprint(json.dumps({"argv":sys.argv[1:],"input":json.load(sys.stdin)}))\n')
        config = {'python': reference(Path(sys.executable).resolve()), 'entrypoint': reference(entrypoint),
                  'sources': [reference(entrypoint)], 'source_commit': 'fixture',
                  'environment': {}, 'timeout_s': 5}
        carrier = PinnedLoopCLI(config)
        result, saved = carrier.call('soodles_loop_inspect', {'request_file': self.request['path']},
                                     self.root / 'transport')
        self.assertEqual(result['argv'], ['manager-request', 'loop_inspect'])
        self.assertEqual(result['input'], {'request_file': self.request['path']})
        self.assertTrue(Path(saved['path']).is_file())
        entrypoint.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source_changed'):
            carrier.call('soodles_loop_inspect', {}, self.root / 'again')
        self.assertFalse((self.root / 'again').exists())

    def test_owner_failure_and_unknown_exit_two_preserve_original_readback(self):
        entrypoint = self.root / 'fixture-cli.py'
        for status in ('failed', 'unknown'):
            with self.subTest(status=status):
                original = {**self.result, 'status': status, 'problem': 'original failure detail'}
                entrypoint.write_text('import json,sys\nprint(' + repr(json.dumps(original)) + ')\nsys.exit(2)\n')
                config = {'python': reference(Path(sys.executable).resolve()), 'entrypoint': reference(entrypoint),
                          'sources': [reference(entrypoint)], 'source_commit': 'fixture',
                          'environment': {}, 'timeout_s': 5}
                adapter = TaskAdapter(self.request, PinnedLoopCLI(config))
                state = adapter.inspect(self.root / ('read-' + status))
                self.assertEqual(state.status, status)
                self.assertEqual(state.result, original)
                self.assertEqual(state.action, original['next'])
                self.assertIsNotNone(state.readback)

    def test_cli_rejects_inspect_with_review(self):
        selection = self.root / 'selection.json'
        selection.write_text(json.dumps({'request': self.request, 'carrier': {}}))
        script = Path(__file__).resolve().parents[1] / 'scripts/run_task_adapter.py'
        run = subprocess.run([sys.executable, str(script), str(selection), 'inspect',
                              str(self.root / 'capture'), '--review', str(selection)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stderr)['problem'], 'inspect_cannot_submit_review')
