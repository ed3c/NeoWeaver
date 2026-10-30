"""Consume original Soodles task continuations without owning their lifecycle.

An integrated task and a source-bound Session observation do not certify
independent acceptance, publication, training, or whole-Goal completion.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess


TOOLS = frozenset({
    'soodles_loop_inspect', 'soodles_loop_enter',
    'soodles_loop_candidate_review', 'soodles_loop_candidate_continue',
    'soodles_loop_retry_host_admission', 'soodles_loop_recover_completion',
})


def _json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate_json_key')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('nonfinite_json')

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def _read(reference):
    if not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}:
        raise ValueError('original_file_reference_required')
    path = Path(reference['path'])
    if not path.is_absolute() or path.resolve() != path or not path.is_file():
        raise ValueError('original_regular_file_required')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256']:
        raise ValueError('source_changed:' + str(path))
    return raw


def _reference(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _mapping(value):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError('invalid_original_task_readback')
    return value


class TransportUnknown(RuntimeError):
    """A call has no validated result; inspect the original task before any write."""


@dataclass(frozen=True, slots=True)
class TaskState:
    status: str
    request: dict
    readback: dict | None
    result: dict
    action: dict | None
    owner_acceptance: str = 'UNKNOWN'
    commit: str | None = None
    cost_usd: None = None
    authorizes_landing: bool = False


class PinnedLoopCLI:
    """Call the selected original CLI; pins establish bytes, not authenticity."""

    def __init__(self, config):
        self.config = deepcopy(config)

    def _verify(self):
        config = self.config
        if config['entrypoint'] not in config['sources'] or not config['sources']:
            raise ValueError('entrypoint_outside_pinned_sources')
        for reference in (config['python'], *config['sources']):
            _read(reference)
        if any(key.startswith(('PYTHON', 'GIT_')) or any(
                word in key.upper() for word in ('TOKEN', 'SECRET', 'PASSWORD', 'API_KEY'))
               for key in config['environment']):
            raise ValueError('unsafe_carrier_environment')
        if not 0 < config['timeout_s']:
            raise ValueError('invalid_carrier_timeout')

    def call(self, tool, arguments, capture):
        if tool not in TOOLS:
            raise ValueError('unsupported_original_tool')
        self._verify()
        config = self.config
        argv = [config['python']['path'], '-B', config['entrypoint']['path']]
        payload = None
        if tool == 'soodles_loop_enter':
            instance = config.get('require_existing_instance')
            if not instance or set(arguments) != {'request_file'}:
                raise ValueError('original_existing_host_required')
            argv += ['loop', 'enter', '--request-file', arguments['request_file'],
                     '--require-existing-instance', instance]
        else:
            argv += ['manager-request', tool.removeprefix('soodles_')]
            payload = json.dumps(arguments, allow_nan=False).encode()
        capture = Path(capture).absolute()
        if capture.is_symlink() or any(parent.is_symlink() for parent in capture.parents):
            raise ValueError('unsafe_capture_directory')
        capture.mkdir()
        (capture / 'transport-input.json').write_text(json.dumps(
            {'tool': tool, 'arguments': arguments, 'source_commit': config['source_commit']},
            ensure_ascii=False, allow_nan=False))
        try:
            with (capture / 'stdout.json').open('xb') as out, (capture / 'stderr.log').open('xb') as err:
                run = subprocess.run(argv, input=payload, stdout=out, stderr=err,
                                     cwd=Path(config['entrypoint']['path']).parent,
                                     env={**config['environment'], 'PYTHONDONTWRITEBYTECODE': '1'},
                                     timeout=config['timeout_s'], check=False)
            self._verify()
            result = _json((capture / 'stdout.json').read_bytes())
            if not isinstance(result, dict) or (run.returncode != 0 and not (
                    run.returncode == 2 and result.get('status') in
                    ('refused', 'failed', 'unknown', 'needs_scope'))):
                raise ValueError('unresolved_original_response')
            return result, _reference(capture / 'stdout.json')
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            raise TransportUnknown('original_call_unresolved:' + str(capture)) from error


class TaskAdapter:
    """One original continuation per call, with Session judgment between calls."""

    def __init__(self, request, carrier):
        self.request = deepcopy(request)
        self.carrier = carrier
        original = _json(_read(self.request))
        if not isinstance(original, dict) or not isinstance(original.get('repository'), str):
            raise ValueError('original_task_request_required')
        repository = Path(original['repository'])
        if not repository.is_absolute():
            raise ValueError('original_absolute_repository_required')
        self.repository = repository.resolve()

    def _state(self, result, readback):
        if result.get('owner') != 'soodles.loop':
            raise ValueError('foreign_task_owner')
        if result.get('request', self.request) != self.request:
            raise ValueError('foreign_original_request')
        inner = _mapping(result.get('inner'))
        progress = _mapping(inner.get('review_progress'))
        report = _mapping(inner.get('acceptance_report'))
        action = result.get('review_input')
        if action is None:
            action = result.get('next')
        if action is not None:
            _mapping(action)
            if action.get('tool') in TOOLS:
                _mapping(action.get('arguments'))
        commit = None
        if report.get('scope') == 'integrated' and report.get('record'):
            record = _json(_read(report['record']))
            if not isinstance(record, dict):
                raise ValueError('invalid_original_acceptance_record')
            commit = record.get('head')
        if result.get('status') in ('unknown', 'refused', 'failed'):
            status = result['status']
        elif result.get('review_input') or (action or {}).get('kind') == 'session_judgment':
            status = 'needs_review'
        elif progress.get('status') == 'locally_integrated':
            status = 'integrated'
        else:
            status = 'waiting'
        return TaskState(status, deepcopy(self.request), readback, deepcopy(result),
                         deepcopy(action), report.get('status', 'UNKNOWN'), commit)

    def _call(self, tool, arguments, capture):
        _read(self.request)
        capture = Path(capture).absolute()
        if (capture == self.repository or self.repository in capture.parents
                or capture in self.repository.parents):
            raise ValueError('capture_overlaps_repository')
        try:
            result, reference = self.carrier.call(tool, arguments, capture)
            _read(self.request)
            return self._state(result, reference)
        except (TransportUnknown, OSError, ValueError) as error:
            return TaskState('unknown', deepcopy(self.request), None,
                             {'problem': str(error), 'capture': str(capture)}, None)

    def inspect(self, capture):
        return self._call('soodles_loop_inspect', {'request_file': self.request['path']}, capture)

    def readback(self, reference):
        return self._state(_json(_read(reference)), deepcopy(reference))

    def advance(self, previous, capture, *, review=None):
        if previous.request != self.request:
            raise ValueError('foreign_original_request')
        capture = Path(capture).absolute()
        if capture.is_symlink() or any(parent.is_symlink() for parent in capture.parents):
            raise ValueError('unsafe_capture_directory')
        if (capture == self.repository or self.repository in capture.parents
                or capture in self.repository.parents):
            raise ValueError('capture_overlaps_repository')
        capture.mkdir()
        current = self.inspect(capture / 'readback')
        if previous.status == 'unknown' or current.status in ('unknown', 'refused', 'failed'):
            return current
        if current.action != previous.action:
            raise ValueError('original_continuation_changed')
        action = current.action
        if not isinstance(action, dict) or action.get('tool') not in TOOLS:
            return current
        arguments = deepcopy(_mapping(action.get('arguments')))
        if arguments.get('request_file') != self.request['path']:
            raise ValueError('foreign_continuation_request')
        if current.status == 'needs_review':
            if review is None:
                return current
            if not isinstance(review, dict) or set(review) - {'decision', 'feedback', 'acceptance_review'}:
                raise ValueError('invalid_session_review')
            if set(review) & (set(arguments) - {'acceptance_review'}):
                raise ValueError('review_replaces_original_binding')
            arguments.update(deepcopy(review))
        elif review is not None:
            raise ValueError('unexpected_session_review')
        return self._call(action['tool'], arguments, capture / 'operation')
