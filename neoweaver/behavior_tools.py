"""JSON readback of original trajectories and externally adjudicated labels.

No scheduler, model execution, selection ledger or artifact mutation lives here.
"""
import json
import sys

from .harness2_adapter import ReviewEvidenceAdapter, read_ref
from .harness_feedback import BehaviorLabel, dataset


def inspect(snapshot, review=None):
    labels = ()
    if review is not None:
        value = read_ref(review)
        if (type(value) is not dict or value.get('schema') != 1
                or value.get('snapshot') != snapshot
                or type(value.get('reviewer')) is not str or not value['reviewer'].strip()
                or type(value.get('cases')) is not list):
            raise ValueError('review must bind this original snapshot and identify its reviewer')
        labels = tuple(BehaviorLabel(**case) for case in value['cases'])
    adapter = ReviewEvidenceAdapter(snapshot, labels)
    from harness2.core.judge import judge_one
    result = judge_one(adapter, adapter.data['run_id'], 'original', 1,
                       'original', adapter.data['run_id'], adapter.spec.runs_root)
    return {'schema': 1, 'status': 'reviewed' if result.graded else 'unknown',
            'snapshot': snapshot, 'review': review, 'dataset': dataset(labels),
            'upstream_judge': {'graded': result.graded, 'fraction': result.frac, 'raw': result.raw,
                               'problem': result.error or None},
            'original_next': adapter.data['original_next'],
            'effects': [], 'authorizes_adoption': False, 'authorizes_training': False,
            'limits': ['Reviewer assertions are preserved, not independently authenticated.',
                       'An observed revision is not a matched improvement experiment.',
                       'Do not expose held-out labels to a proposer or use them for selection.']}


def main():
    try:
        request = json.load(sys.stdin)
        if type(request) is not dict or not {'snapshot'} <= request.keys() or request.keys() - {'snapshot', 'review'}:
            raise ValueError('expected snapshot and optional review references')
        result = inspect(**request)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({'status': 'refused', 'problem': str(error), 'effects': [], 'authorizes_adoption': False}))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
