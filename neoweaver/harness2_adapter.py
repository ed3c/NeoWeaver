"""Read-only seam to upstream Harness2 context and post-selection judge APIs.

The caller installs the pinned optional upstream package. The adapter never uses
Harness2's executor or selection pool: Noodle owns runs; outer owns adoption.
"""
import base64
import hashlib
import json
from pathlib import Path

from .harness_feedback import BehaviorLabel, dataset

UPSTREAM = '1cfe254e8d25b15f37048c3730134686abe60335'


def read_ref(reference):
    if (type(reference) is not dict or set(reference) != {'path', 'sha256'}
            or type(reference['path']) is not str or not Path(reference['path']).is_absolute()
            or type(reference['sha256']) is not str):
        raise ValueError('original absolute file reference required')
    path = Path(reference['path'])
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256']:
        raise ValueError('source drift: ' + str(path))
    return json.loads(raw)


class ReviewEvidenceAdapter:
    """Consumes a Soodles trajectory snapshot; labels stay out of model context."""

    def __init__(self, snapshot, labels=(), *, historical=False):
        if type(historical) is not bool:
            raise ValueError('historical must be explicit boolean')
        self.historical = historical
        self.reference = snapshot
        self.data = read_ref(snapshot)
        if type(self.data) is not dict or self.data.get('kind') != 'original_loop_behavior':
            raise ValueError('original LoopManager behavior snapshot required')
        if historical and type(self.data.get('retained_sources')) is not list:
            raise ValueError('snapshot has no retained source bytes')
        for ref in [self.data['request'], *self.data['sources']]:
            self.source_bytes(ref)
        self.labels = labels
        dataset(labels)  # Validate labels before the upstream judge catches errors.
        from harness2.core.spec import BenchSpec, BenchPrompts, ChannelSpec
        self.spec = BenchSpec('soodles-review', Path(snapshot['path']).parent, 'codex_root',
            BenchPrompts(work='Review a candidate against the original task and preserve its continuation.'),
            {'proposer': ChannelSpec('opencode', 'unused/read-only'),
             'selector': ChannelSpec('opencode', 'unused/read-only')}, allow_subagents=False)

    def source_bytes(self, ref):
        row = next((x for x in self.data.get('retained_sources', []) if x['reference'] == ref), None)
        if self.historical:
            if row is None:
                raise ValueError('historical source missing: ' + ref['path'])
            raw = base64.b64decode(row['base64'], validate=True)
        else:
            raw = Path(ref['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref['sha256']:
            raise ValueError('source drift: ' + ref['path'])
        return raw

    def _task(self, task_id):
        if task_id != self.data['run_id']:
            raise ValueError('foreign task')

    def _run(self, run_dir):
        if Path(run_dir).resolve() != Path(self.reference['path']).parent.resolve():
            raise ValueError('foreign original run')
        if read_ref(self.reference) != self.data:
            raise ValueError('snapshot changed')
        for ref in [self.data['request'], *self.data['sources']]:
            self.source_bytes(ref)

    def task_prompt(self, task_id):
        self._task(task_id)
        return self.data['goal']

    def task_files(self, task_id):
        self._task(task_id)
        return None  # Never expose evaluator labels, fixtures or held-out keys.

    def trajectory(self, run_dir, *, obs_trunc):
        self._run(run_dir)
        # No label/reward is passed into the improvement context. Raw native
        # traces remain original sources; no prompt-budget truncation is applied.
        parts = []
        for ref in self.data['native_traces']:
            raw = self.source_bytes(ref)
            parts.append(raw.decode('utf-8'))
        if not parts:
            raise ValueError('native trace unavailable')
        return '\n'.join(parts)

    def deliverable_text(self, run_dir):
        self._run(run_dir)
        return json.dumps({'nodes': self.data['nodes'], 'edges': self.data['edges'],
                           'findings': self.data['findings'], 'original_next': self.data['original_next']},
                          ensure_ascii=False, indent=2)

    def score(self, run_dir, task_id):
        self._task(task_id)
        self._run(run_dir)
        rows = dataset(self.labels)['cases']
        if not rows or any(row['reward'] is None for row in rows):
            return None
        passed = sum(row['reward'] for row in rows)
        return {'n_passed': passed, 'n_criteria': len(rows), 'all_pass': passed == len(rows),
                'evidence_ceiling': 'SUPPLIED_REVIEW_FACTS', 'authorizes_adoption': False}

    def execute(self, *args, **kwargs):
        raise RuntimeError('Consume the original LoopManager next; this evidence adapter cannot dispatch.')
