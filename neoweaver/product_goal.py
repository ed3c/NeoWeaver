"""Read-only Goal reconciliation over original TaskAdapter observations.

Coverage is a Session semantic choice. Neither that choice nor this projection
certifies the original Owner, independent acceptance, or the whole product.
"""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

from neoweaver.task_adapter import TaskAdapter, _json, _read


def object_fields(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ValueError('invalid_fields:' + ','.join(required))
    return value


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('invalid_' + field)
    return value


def repository(value):
    path = Path(text(value, 'repository'))
    if not path.is_absolute() or path.resolve() != path or not path.is_dir():
        raise ValueError('selected_absolute_repository_required')
    return path


def load_selection(selection):
    object_fields(selection, ('profile', 'repository', 'goal', 'requirements', 'tasks'),
                  ('coverage', 'sources', 'baseline'))
    repo = repository(selection['repository'])
    if selection['profile'] not in ('generic', 'neoweaver'):
        raise ValueError('unsupported_product_profile')
    goal = _read(selection['goal']).decode('utf-8')
    record = _json(_read(selection['requirements']))
    if not isinstance(record, dict) or not isinstance(record.get('requirements'), list) or not record['requirements']:
        raise ValueError('original_requirements_required')
    requirements = record['requirements']
    ids = [text(row.get('id'), 'requirement_id') for row in requirements if isinstance(row, dict)]
    if len(ids) != len(requirements) or len(set(ids)) != len(ids):
        raise ValueError('invalid_requirement_identities')
    for field in ('goal', 'requirements'):
        if repo not in Path(selection[field]['path']).parents:
            raise ValueError('product_source_repository_mismatch')
    if selection['profile'] == 'neoweaver':
        expected = {'goal': repo / 'docs/specs/neoweaver-product-program.md',
                    'requirements': repo / 'docs/compiled/specification.json'}
        if any(Path(selection[key]['path']) != path for key, path in expected.items()):
            raise ValueError('wrong_neoweaver_goal_source')
        if len(requirements) != 10 or len(record.get('cards', [])) != 44:
            raise ValueError('incomplete_neoweaver_knowledge_record')
    sources = selection.get('sources', [])
    if not isinstance(sources, list):
        raise ValueError('invalid_sources')
    source_text = [{'reference': ref, 'text': _read(ref).decode('utf-8')} for ref in sources]
    if not isinstance(selection['tasks'], dict):
        raise ValueError('invalid_original_tasks')
    adapters = {}
    for name, task in selection['tasks'].items():
        text(name, 'task_name')
        object_fields(task, ('request',), ('readback', 'carrier'))
        adapters[name] = TaskAdapter(task['request'], None)
    coverage = selection.get('coverage')
    if coverage is not None:
        if not isinstance(coverage, list):
            raise ValueError('invalid_coverage')
        seen = set()
        for row in coverage:
            object_fields(row, ('requirement', 'clause', 'task', 'relation'))
            text(row['clause'], 'coverage_clause')
            if row['requirement'] not in ids or row['task'] not in adapters:
                raise ValueError('unknown_coverage_reference')
            if row['relation'] not in ('product', 'dependency'):
                raise ValueError('invalid_coverage_relation')
            if row['relation'] == 'product' and adapters[row['task']].repository != repo:
                raise ValueError('task_product_repository_mismatch')
            key = (row['requirement'], row['clause'], row['task'])
            if key in seen:
                raise ValueError('duplicate_coverage')
            seen.add(key)
    baseline = selection.get('baseline', {})
    if not isinstance(baseline, dict) or set(baseline) - set(adapters):
        raise ValueError('invalid_baseline_tasks')
    return goal, record, source_text, adapters


def local_status(state):
    result = state.result
    if state.status == 'unknown':
        return 'unknown'
    if state.status in ('refused', 'failed') or result.get('status') in ('blocked', 'needs_scope', 'refused', 'failed'):
        return 'blocked'
    if state.status == 'needs_review':
        return 'needs_input'
    report = (result.get('inner') or {}).get('acceptance_report') or {}
    if (state.status == 'integrated' and state.owner_acceptance == 'PASS'
            and report.get('scope') == 'integrated' and state.commit and report.get('record')):
        return 'locally_completed'
    if state.status == 'integrated' or result.get('status') == 'completed':
        return 'pending_verification'
    return 'pending'


def coverage_schema(requirements, tasks):
    return {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
        'required': ['requirement', 'clause', 'task', 'relation'], 'properties': {
            'requirement': {'type': 'string', 'enum': [r['id'] for r in requirements]},
            'clause': {'type': 'string', 'minLength': 1},
            'task': {'type': 'string', 'enum': list(tasks)},
            'relation': {'enum': ['product', 'dependency']}}}}


def reconcile(selection, observations=None):
    goal, record, sources, adapters = load_selection(selection)
    states = {}
    for name, adapter in adapters.items():
        task = selection['tasks'][name]
        if observations is not None and name in observations:
            states[name] = observations[name]
        elif observations is None and task.get('readback'):
            states[name] = adapter.readback(task['readback'])
    obligations = []
    for row in selection.get('coverage') or []:
        state = states.get(row['task'])
        status = local_status(state) if state else 'unknown'
        obligations.append({**row, 'status': status,
                            'evidence_ceiling': 'ORIGINAL_OWNER_READBACK_WITH_SESSION_COVERAGE',
                            'readback': state.readback if state else None})
    refreshed_selection = deepcopy(selection)
    baseline = deepcopy(selection.get('baseline', {}))
    for name, state in states.items():
        previous_ref = selection['tasks'][name].get('readback')
        if observations is not None and name in observations and previous_ref:
            baseline[name] = previous_ref
        if state.readback:
            refreshed_selection['tasks'][name]['readback'] = state.readback
        else:
            refreshed_selection['tasks'][name].pop('readback', None)
    refreshed_selection['baseline'] = baseline
    changes = []
    for name, previous in baseline.items():
        before = adapters[name].readback(previous)
        after = states.get(name)
        if after and before.result != after.result:
            changes.append({'task': name, 'before': local_status(before),
                            'after': local_status(after), 'previous': previous,
                            'current': after.readback})
    inputs = []
    if 'coverage' not in selection:
        inputs.append({'name': 'goal_coverage', 'reason': 'Session_selects_applicable_local_clauses',
                       'input_schema': coverage_schema(record['requirements'], adapters)})
    for name in adapters:
        state = states.get(name)
        if not state:
            inputs.append({'name': 'owner_readback', 'task': name,
                           'reason': 'original_task_observation_missing',
                           'operation': 'goal_refresh'})
        elif state.status == 'needs_review':
            inputs.append({'name': 'session_review', 'task': name, 'evidence': asdict(state),
                           'input_schema': REVIEW_SCHEMA})
        elif state.status == 'unknown':
            inputs.append({'name': 'original_owner_readback', 'task': name,
                           'reason': state.result, 'operation': 'goal_refresh'})
    return {'status': 'needs_input' if inputs else 'reconciled',
            'profile': selection['profile'], 'repository': selection['repository'],
            'selection': refreshed_selection,
            'goal': {'reference': selection['goal'], 'text': goal},
            'knowledge_record': record, 'additional_sources': sources,
            'obligations': obligations, 'changes': changes,
            'locally_completed': [r for r in obligations if r['status'] == 'locally_completed' and r['relation'] == 'product'],
            'dependency_completed': [r for r in obligations if r['status'] == 'locally_completed' and r['relation'] == 'dependency'],
            'pending_verification': [r for r in obligations if r['status'] == 'pending_verification'],
            'blocked': [r for r in obligations if r['status'] == 'blocked'],
            'unknown': [r for r in obligations if r['status'] == 'unknown'],
            'remaining_requirements': record['requirements'],
            'uncovered_requirements': [r['id'] for r in record['requirements'] if r['id'] not in {o['requirement'] for o in obligations}],
            'owner_states': {name: asdict(state) for name, state in states.items()},
            'next': {name: state.action for name, state in states.items()},
            'needs_input': inputs, 'whole_goal': 'OPEN', 'authorizes_landing': False}


REVIEW_SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'decision': {'type': 'string'}, 'feedback': {'type': 'string'},
    'acceptance_review': {'type': 'object'}}}
