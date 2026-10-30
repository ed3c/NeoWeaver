"""Single product operation registry shared by CLI and MCP transports."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

from neoweaver.learning import TrainingCandidate, inspect_training_candidate, _ALLOWED
from neoweaver.product_goal import load_selection, reconcile, REVIEW_SCHEMA
from neoweaver.task_adapter import PinnedLoopCLI, TaskAdapter, TOOLS


def obj(properties, required=()):
    return {'type': 'object', 'properties': properties, 'required': list(required),
            'additionalProperties': False}


STRING = {'type': 'string', 'minLength': 1}
REF = obj({'path': STRING, 'sha256': STRING}, ('path', 'sha256'))
CARRIER = obj({'python': REF, 'entrypoint': REF, 'sources': {'type': 'array', 'items': REF, 'minItems': 1},
               'source_commit': STRING, 'environment': {'type': 'object'},
               'timeout_s': {'type': 'number', 'exclusiveMinimum': 0},
               'require_existing_instance': STRING},
              ('python', 'entrypoint', 'sources', 'source_commit', 'environment', 'timeout_s'))
TASK = obj({'request': REF, 'readback': REF, 'carrier': CARRIER}, ('request',))
COVERAGE = obj({'requirement': STRING, 'clause': STRING, 'task': STRING,
                'relation': {'type': 'string', 'enum': ['product', 'dependency']}},
               ('requirement', 'clause', 'task', 'relation'))
SELECTION = obj({'profile': {'enum': ['generic', 'neoweaver']}, 'repository': STRING,
                 'goal': REF, 'requirements': REF,
                 'sources': {'type': 'array', 'items': REF},
                 'tasks': {'type': 'object', 'additionalProperties': TASK},
                 'coverage': {'type': 'array', 'items': COVERAGE},
                 'baseline': {'type': 'object', 'additionalProperties': REF}},
                ('profile', 'repository', 'goal', 'requirements', 'tasks'))


def validate(value, schema, at='arguments'):
    kind = schema.get('type')
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'boolean': type(value) is bool,
             'integer': type(value) is int, 'number': type(value) in (int, float)}
    if kind and not valid[kind]:
        raise ValueError('invalid_type:' + at)
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError('invalid_choice:' + at)
    if kind == 'object':
        props = schema.get('properties', {})
        if set(schema.get('required', [])) - set(value):
            raise ValueError('missing_fields:' + at + ':' + ','.join(sorted(set(schema['required']) - set(value))))
        additional = schema.get('additionalProperties', True)
        for key, child in value.items():
            if key in props:
                validate(child, props[key], at + '.' + key)
            elif additional is False:
                raise ValueError('unexpected_field:' + at + '.' + key)
            elif isinstance(additional, dict):
                validate(child, additional, at + '.' + key)
    if kind == 'array':
        if len(value) < schema.get('minItems', 0):
            raise ValueError('empty_array:' + at)
        for index, child in enumerate(value):
            validate(child, schema.get('items', {}), at + '[' + str(index) + ']')
    if kind == 'string' and len(value.strip()) < schema.get('minLength', 0):
        raise ValueError('empty_string:' + at)
    if kind in ('integer', 'number'):
        if value < schema.get('minimum', value) or value > schema.get('maximum', value):
            raise ValueError('out_of_range:' + at)
        if 'exclusiveMinimum' in schema and value <= schema['exclusiveMinimum']:
            raise ValueError('out_of_range:' + at)


def refused(error):
    return {'status': 'refused', 'problem': str(error), 'authorizes_landing': False}


def carrier_adapter(selection, name):
    _, _, _, adapters = load_selection(selection)
    if name not in adapters:
        raise ValueError('unknown_selected_task')
    task = selection['tasks'][name]
    if 'carrier' not in task:
        raise ValueError('original_carrier_missing')
    return TaskAdapter(task['request'], PinnedLoopCLI(task['carrier']))


def goal_reconcile(selection):
    return reconcile(selection)


def goal_refresh(selection, capture):
    _, _, _, adapters = load_selection(selection)
    carriers = {}
    unavailable = []
    for name in adapters:
        if 'carrier' not in selection['tasks'][name]:
            unavailable.append({'name': 'original_carrier', 'task': name,
                                'reason': 'original_carrier_missing', 'input_schema': CARRIER})
        else:
            carriers[name] = carrier_adapter(selection, name)
    if not carriers:
        result = reconcile(selection, {})
        result['needs_input'].extend(unavailable)
        result['status'] = 'needs_input'
        return result
    root = Path(capture)
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('absolute_canonical_capture_required')
    for adapter in adapters.values():
        if root == adapter.repository or root in adapter.repository.parents or adapter.repository in root.parents:
            raise ValueError('capture_overlaps_repository')
    if root == Path(selection['repository']) or Path(selection['repository']) in root.parents:
        raise ValueError('capture_overlaps_product_repository')
    try:
        root.mkdir()
    except FileExistsError:
        return {'status': 'unknown', 'problem': 'capture_exists_read_original_owner',
                'capture': capture, 'next': {'operation': 'goal_refresh', 'requires': 'fresh_external_capture'},
                'authorizes_landing': False}
    states = {name: adapter.inspect(root / str(index))
              for index, (name, adapter) in enumerate(carriers.items())}
    try:
        result = reconcile(selection, states)
        result['needs_input'].extend(unavailable)
        if unavailable:
            result['status'] = 'needs_input'
        return result
    except (OSError, ValueError, UnicodeError) as error:
        return {'status': 'unknown', 'problem': 'source_changed_after_owner_read:' + str(error),
                'owner_states': {name: asdict(state) for name, state in states.items()},
                'authorizes_landing': False}


def task_continue(selection, task, capture, review=None, dry_run=False, max_steps=16):
    _, _, _, adapters = load_selection(selection)
    if task not in adapters:
        raise ValueError('unknown_selected_task')
    adapter = adapters[task]
    selected = selection['tasks'][task]
    if 'readback' not in selected:
        raise ValueError('original_readback_required_before_continue')
    previous = adapter.readback(selected['readback'])
    if dry_run:
        return {'status': 'dry_run', 'task': asdict(previous), 'next': previous.action,
                'needs_input': previous.result.get('review_input'), 'authorizes_landing': False}
    adapter = carrier_adapter(selection, task)
    root = Path(capture)
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('absolute_canonical_capture_required')
    product_repo = Path(selection['repository'])
    if root == product_repo or product_repo in root.parents or root in product_repo.parents:
        raise ValueError('capture_overlaps_product_repository')
    if root == adapter.repository or adapter.repository in root.parents or root in adapter.repository.parents:
        raise ValueError('capture_overlaps_repository')
    try:
        root.mkdir()
    except FileExistsError:
        return {'status': 'unknown', 'problem': 'capture_exists_read_original_owner',
                'capture': capture, 'next': {'operation': 'goal_refresh', 'requires': 'fresh_external_capture'},
                'authorizes_landing': False}
    trace = []
    state = previous
    boundary = 'step_limit'
    for index in range(max_steps):
        before = state
        state = adapter.advance(state, root / str(index), review=review)
        review = None
        trace.append(asdict(state))
        if before.status == 'unknown':
            boundary = 'unknown_readback_only'
            break
        if state.status in ('unknown', 'refused', 'failed', 'needs_review'):
            boundary = state.status
            break
        if state.result.get('status') in ('blocked', 'needs_scope'):
            boundary = 'original_owner_blocked'
            break
        if not state.action or state.action.get('tool') not in TOOLS:
            boundary = 'original_owner_boundary'
            break
        if state.action == before.action or state.action.get('tool') == 'soodles_loop_inspect':
            boundary = 'original_owner_wait'
            break
    try:
        projection = reconcile(selection, {task: state})
    except (OSError, ValueError, UnicodeError) as error:
        return {'status': 'unknown', 'problem': 'source_changed_after_owner_call:' + str(error),
                'task': asdict(state), 'trace': trace, 'authorizes_landing': False}
    return {'status': state.status, 'boundary': boundary, 'task': asdict(state),
            'trace': trace, 'next': state.action, 'product': projection,
            'authorizes_landing': False}


def training_inspect(facts):
    return asdict(inspect_training_candidate(TrainingCandidate(**facts)))


OPERATIONS = {
    'goal_reconcile': (goal_reconcile, obj({'selection': SELECTION}, ('selection',)),
                       'Read selected Goal, full requirements and original task readbacks; return scoped differences.'),
    'goal_refresh': (goal_refresh, obj({'selection': SELECTION, 'capture': STRING}, ('selection', 'capture')),
                     'Inspect original Owners into fresh external captures and reconcile their current observations.'),
    'task_continue': (task_continue, obj({'selection': SELECTION, 'task': STRING, 'capture': STRING,
                        'review': REVIEW_SCHEMA, 'dry_run': {'type': 'boolean'},
                        'max_steps': {'type': 'integer', 'minimum': 1, 'maximum': 64}},
                        ('selection', 'task', 'capture')),
                      'Consume original TaskAdapter continuations to a Session, wait, permission or unknown boundary.'),
    'training_inspect': (training_inspect, obj({'facts': obj({key: {'type': 'string', 'enum': list(values)}
                         for key, values in _ALLOWED.items()}, tuple(_ALLOWED))}, ('facts',)),
                         'Use existing deterministic A6 typed-fact screen; never authorize training.'),
}


def operation_schemas():
    return [{'name': name, 'description': description, 'inputSchema': deepcopy(schema)}
            for name, (_, schema, description) in OPERATIONS.items()]


def execute(name, arguments):
    if name not in OPERATIONS:
        return refused('unknown_operation')
    handler, schema, _ = OPERATIONS[name]
    try:
        validate(arguments, schema)
        return handler(**arguments)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        return refused(error)
