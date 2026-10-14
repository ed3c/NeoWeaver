"""Literal Codex protocol fixtures, not live native evidence."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from neoweaver.native import (DecisionOracle, FixedConditions, NativeRefusal,
                              NativeTask, inspect_native_pair, run_native_arm)
from neoweaver.patches import OwnerRef
from neoweaver.snapshot import SourceFile, SourceManifest, StagedSource, StagedSourcePair


ANSWER = b'{"decisions":[{"case":"c1","classification":"ParsedProposal","condition":null},{"case":"c2","classification":"DiagnosticRefusal","condition":"duplicate_json_key"},{"case":"c3","classification":"DiagnosticRefusal","condition":"protected_target"}]}'
POPULATION = b'[{"case":"c1","raw":"fixture one"},{"case":"c2","raw":"fixture two"},{"case":"c3","raw":"fixture three"}]'
THREAD = b'{"type":"thread.started","thread_id":"fixture-thread"}\n'
WARNING = b'{"type":"item.completed","item":{"id":"item_0","type":"error","message":"clamping SessionEnd hook timeout to 3s"}}\n'
START = b'{"type":"turn.started"}\n'
COMMENT = b'{"type":"item.completed","item":{"id":"item_1","type":"agent_message","text":"I will inspect the source."}}\n'
END = b'{"type":"turn.completed","usage":{"input_tokens":123,"output_tokens":45}}\n'


def message(answer):
    return json.dumps({"type": "item.completed", "item": {
        "id": "item_2", "type": "agent_message", "text": answer.decode()}}).encode() + b'\n'


def completed(answer=ANSWER):
    return THREAD + WARNING + START + COMMENT + message(answer) + END


class NativeFixture:
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        checksum = hashlib.sha256(b"pinned\n").hexdigest()
        manifest = SourceManifest((SourceFile("code.txt", checksum, False),),
                                  hashlib.sha256(b"code.txt\0-" + bytes.fromhex(checksum)).hexdigest())
        sources = []
        for arm in ("baseline", "candidate"):
            root = self.root / arm
            root.mkdir()
            (root / "code.txt").write_bytes(b"pinned\n")
            sources.append(StagedSource(root, manifest))
        self.pair = StagedSourcePair("a" * 40, "b" * 40, *sources)
        self.task = NativeTask(Path('/usr/bin/true'), "selected-model", "high",
                               b"Read the cases; return decisions.", b'{"type":"object"}',
                               POPULATION, 30, "Provider default; realized seed unknown")
        self.conditions = FixedConditions(*(OwnerRef("fixture", x) for x in (
            "snapshot", "task", "environment", "solver", "seed-policy", "budget", "H0", "H0")))
        self.oracle = DecisionOracle(self.task, ANSWER, OwnerRef("verification", "fixed-oracle"))
        self.counter = 0

    def capture(self, raw=None, answer=ANSWER, arm="baseline", task=None,
                exit_code=0, timeout=False, source_drift=False, thread=None, conditions=None):
        raw = completed(answer) if raw is None else raw
        if thread:
            raw = raw.replace(b"fixture-thread", thread.encode())
        directory = self.root / ("capture-" + str(self.counter))
        self.counter += 1
        def execute(argv, **kwargs):
            self.assertEqual(kwargs['cwd'], getattr(self.pair, arm).directory)
            self.assertEqual(kwargs['input'], (task or self.task).prompt)
            self.assertNotIn('shell', kwargs)
            kwargs['stdout'].write(raw)
            kwargs['stderr'].write(b"actual stderr fixture")
            if answer is not None:
                Path(argv[argv.index('--output-last-message') + 1]).write_bytes(answer + b'\n')
            if source_drift:
                (self.pair.baseline.directory / 'code.txt').write_bytes(b'drift')
            if timeout:
                raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
            return subprocess.CompletedProcess(argv, exit_code)
        with patch('neoweaver.native.subprocess.run', side_effect=execute) as launch:
            capture = run_native_arm(self.pair, arm, task or self.task,
                                     conditions or self.conditions, directory)
        self.assertEqual(launch.call_count, 1)
        return capture

    def inspect(self, capture, oracle=None):
        return inspect_native_pair(capture, capture, oracle or self.oracle).oracle_results[0]


class NativeTests(NativeFixture, unittest.TestCase):
    def test_completed_final_and_output_file_match(self):
        capture = self.capture()
        result = self.inspect(capture)
        self.assertEqual((result.status, result.completed, result.thread_id, result.terminal),
                         ('MATCH_SCOPED', True, 'fixture-thread', 'completed'))
        self.assertEqual(result.usage, (('input_tokens', 123), ('output_tokens', 45)))
        self.assertIs(result.capture, capture)
        self.assertIs(result.oracle, self.oracle)
        self.assertEqual(capture.raw, completed())
        self.assertEqual(capture.stderr, b'actual stderr fixture')
        self.assertEqual(capture.exit_code, 0)
        self.assertEqual(capture.directory.stat().st_mode & 0o077, 0)
        self.assertFalse(capture.isolation_verified)
        self.assertEqual(capture.effect_status, 'unknown')
        self.assertIn('read-only', capture.argv)
        self.assertIn('approval_policy="never"', capture.argv)
        self.assertIn('model_reasoning_effort="high"', capture.argv)
        self.assertIn('--skip-git-repo-check', capture.argv)
        self.assertNotIn(self.oracle.expected, (capture.directory / 'launch.json').read_bytes())

    def test_unavailable_partial_failed_and_process_exit_are_not_completion(self):
        for raw, answer, exit_code, timeout in [
            (b'', ANSWER, 0, False),
            (THREAD + START + COMMENT, ANSWER, 0, False),
            (THREAD + START + message(ANSWER), ANSWER, 0, False),
            (THREAD + START + message(ANSWER) + b'{"type":"turn.failed","error":{"message":"provider failure"}}\n', ANSWER, 1, False),
            (completed(), None, 0, False),
            (completed(), ANSWER, 1, False),
            (THREAD + START + COMMENT, None, 0, True),
            (THREAD + START + b'{"type":"error","message":"provider unavailable"}\n', None, 1, False),
        ]:
            with self.subTest(raw=raw, exit=exit_code, timeout=timeout):
                capture = self.capture(raw=raw, answer=answer, exit_code=exit_code, timeout=timeout)
                result = self.inspect(capture)
                self.assertEqual((result.status, result.completed), ('INCONCLUSIVE', None))
                self.assertEqual(capture.raw, raw)
                self.assertEqual(capture.timed_out, timeout)

    def test_malformed_repeated_and_contradictory_protocol_refuses(self):
        cases = [
            (THREAD + THREAD + START, 'repeated_or_invalid_thread'),
            (THREAD + START + START, 'repeated_or_invalid_turn'),
            (completed() + END, 'event_after_terminal'),
            (THREAD + START + message(ANSWER) + message(ANSWER) + END, 'repeated_completed_item'),
            (THREAD + b'{"type":"turn.started","thread_id":"different"}\n', 'contradictory_thread'),
            (THREAD + b'{"type":"turn.started","turn_id":"a"}\n' + b'{"type":"turn.completed","turn_id":"b"}\n', 'contradictory_turn'),
            (THREAD + START + b'{bad\n', 'malformed_json'),
            (THREAD + START + b'\n', 'malformed_ndjson'),
            (START, 'event_before_thread'),
            (THREAD + END, 'terminal_outside_turn'),
            (THREAD + START + b'{"type":"future.event"}\n', 'unsupported_event'),
            (THREAD + START + message(ANSWER) + b'{"type":"turn.completed","usage":{"input_tokens":true}}\n', 'malformed_usage'),
        ]
        for raw, reason in cases:
            with self.subTest(reason=reason):
                result = self.inspect(self.capture(raw=raw))
                self.assertEqual((result.status, result.reasons, result.completed), ('REFUSED', (reason,), None))

    def test_unfinished_and_contradictory_item_lifecycle_refuses(self):
        started = b'{"type":"item.started","item":{"id":"cmd","type":"command_execution","status":"in_progress"}}\n'
        updated = b'{"type":"item.updated","item":{"id":"cmd","type":"command_execution","status":"in_progress"}}\n'
        finished = b'{"type":"item.completed","item":{"id":"cmd","type":"command_execution","status":"completed"}}\n'
        for items, reason in (
            (started, 'unfinished_items_at_completion'),
            (started + started, 'repeated_started_item'),
            (updated, 'update_without_started_item'),
            (started + finished.replace(b'command_execution', b'agent_message'), 'contradictory_item_type'),
            (started + finished.replace(b'completed"}}', b'in_progress"}}'), 'contradictory_item_status'),
        ):
            with self.subTest(reason=reason):
                result = self.inspect(self.capture(raw=THREAD + START + items + message(ANSWER) + END))
                self.assertEqual((result.status, result.reasons), ('REFUSED', (reason,)))
        result = self.inspect(self.capture(raw=THREAD + START + started + updated + finished + message(ANSWER) + END))
        self.assertEqual(result.status, 'MATCH_SCOPED')

    def test_lone_unicode_surrogate_is_malformed_instead_of_crashing(self):
        raw = THREAD + START + b'{"type":"item.completed","item":{"id":"bad","type":"agent_message","text":"\\ud800"}}\n' + END
        result = self.inspect(self.capture(raw=raw))
        self.assertEqual((result.status, result.reasons), ('REFUSED', ('malformed_agent_message',)))

    def test_parent_traversal_cannot_place_capture_inside_source(self):
        sibling = self.root / 'sibling'
        sibling.mkdir()
        directory = sibling / '..' / 'baseline' / 'hidden-capture'
        with patch('neoweaver.native.subprocess.run') as launch, self.assertRaisesRegex(NativeRefusal, 'capture_exists_or_overlaps_source'):
            run_native_arm(self.pair, 'baseline', self.task, self.conditions, directory)
        launch.assert_not_called()
        self.assertFalse((self.pair.baseline.directory / 'hidden-capture').exists())

    def test_output_file_must_match_last_message_not_an_earlier_answer(self):
        for raw in (completed(), THREAD + START + message(ANSWER) + COMMENT + END):
            result = self.inspect(self.capture(raw=raw, answer=b'{}'))
            self.assertEqual((result.status, result.reasons), ('REFUSED', ('last_message_mismatch',)))

    def test_literal_wrong_condition_is_valid_scoped_failure(self):
        result = self.inspect(self.capture(answer=ANSWER.replace(b'duplicate_json_key', b'protected_target')))
        self.assertEqual((result.status, result.completed, result.reasons),
                         ('FAIL_SCOPED', False, ('decision_mismatch:c2',)))

    def test_response_shape_and_population_refuse(self):
        rows = json.loads(ANSWER)['decisions']
        cases = [
            (b'{"decisions":[],"decisions":[]}', 'duplicate_json_key'),
            (b'{"decisions":[]}', 'case_population_mismatch'),
            (b'{}', 'invalid_decision_shape'),
            (b'{"decisions":null}', 'invalid_decision_shape'),
            (json.dumps({'decisions': rows + rows[:1]}).encode(), 'repeated_case'),
            (json.dumps({'decisions': rows[:2]}).encode(), 'case_population_mismatch'),
            (json.dumps({'decisions': rows + [{'case':'extra','classification':'ParsedProposal','condition':None}]}).encode(), 'case_population_mismatch'),
            (ANSWER.replace(b'"condition":null', b'"condition":false'), 'invalid_decision_shape'),
            (ANSWER.replace(b'"condition":null', b'"condition":null,"extra":true'), 'invalid_decision_shape'),
            (b'I checked all cases.', 'malformed_json'),
        ]
        for answer, reason in cases:
            with self.subTest(reason=reason):
                result = self.inspect(self.capture(answer=answer))
                self.assertEqual((result.status, result.reasons), ('REFUSED', (reason,)))

    def test_case_order_does_not_change_oracle(self):
        answer = json.dumps({'decisions': list(reversed(json.loads(ANSWER)['decisions']))}).encode()
        self.assertEqual(self.inspect(self.capture(answer=answer)).status, 'MATCH_SCOPED')

    def test_capture_raw_launch_and_last_message_drift_refuse(self):
        for name in ('launch.json', 'process.json', 'raw.ndjson', 'stderr.bin', 'last-message.txt', 'prompt.txt', 'schema.json', 'population.json'):
            with self.subTest(name=name):
                capture = self.capture()
                (capture.directory / name).write_bytes(b'drift')
                self.assertEqual(self.inspect(capture).reasons, ('capture_drift',))

    def test_dataclass_relabel_cannot_replace_persisted_launch(self):
        capture = self.capture()
        for changed in (replace(capture, task=replace(self.task, model='other')),
                        replace(capture, conditions=replace(self.conditions, task_ref=OwnerRef('fake', 'other'))),
                        replace(capture, source=replace(self.pair, commit='c' * 40)),
                        replace(capture, arm='candidate')):
            self.assertEqual(self.inspect(changed).reasons, ('capture_drift',))

    def test_source_drift_during_and_after_launch_refuses_without_refresh(self):
        capture = self.capture(source_drift=True)
        self.assertEqual(capture.source_error, 'source_changed')
        self.assertEqual(self.inspect(capture).reasons, ('source_changed',))
        (self.pair.baseline.directory / 'code.txt').write_bytes(b'pinned\n')
        capture = self.capture()
        (self.pair.candidate.directory / 'code.txt').write_bytes(b'drift')
        self.assertEqual(self.inspect(capture).reasons, ('source_changed',))

    def test_source_overlap_symlink_and_capture_reuse_refuse_before_launch(self):
        capture = self.capture()
        bad_pairs = [replace(self.pair, candidate=self.pair.baseline)]
        for pair in bad_pairs:
            with patch('neoweaver.native.subprocess.run') as launch, self.assertRaises(NativeRefusal):
                run_native_arm(pair, 'baseline', self.task, self.conditions, self.root / 'new')
            launch.assert_not_called()
        for destination in (capture.directory, self.pair.candidate.directory / 'output'):
            with patch('neoweaver.native.subprocess.run') as launch, self.assertRaises(NativeRefusal):
                run_native_arm(self.pair, 'baseline', self.task, self.conditions, destination)
            launch.assert_not_called()
        link = self.root / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(NativeRefusal, 'symlink_capture_directory'):
            run_native_arm(self.pair, 'baseline', self.task, self.conditions, link / 'new')
        (self.pair.baseline.directory / 'evil').symlink_to('code.txt')
        with self.assertRaisesRegex(NativeRefusal, 'source_symlink'):
            run_native_arm(self.pair, 'baseline', self.task, self.conditions, self.root / 'new')

    def test_launch_unavailable_preserves_actual_error_without_retry(self):
        with patch('neoweaver.native.subprocess.run', side_effect=OSError('fixture launch failure')) as launch:
            capture = run_native_arm(self.pair, 'baseline', self.task, self.conditions, self.root / 'unavailable')
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(capture.launch_error, 'fixture launch failure')
        self.assertIsNone(capture.exit_code)
        self.assertEqual(self.inspect(capture).status, 'INCONCLUSIVE')


if __name__ == '__main__':
    unittest.main()
