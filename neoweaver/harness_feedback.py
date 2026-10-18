"""Independent labels and bounded feedback for frozen-model Harness changes.

Inputs are supplied evaluation facts. This module cannot authenticate a reviewer
or prove its semantic judgment. No model, worker, training or adoption is started.
"""
from dataclasses import dataclass

from .replay import PairInspection


@dataclass(frozen=True, slots=True)
class BehaviorLabel:
    case_id: str
    partition: str
    outcome: str  # pass / fail / unknown, adjudicated against original requirements
    criteria_supported: bool
    independent_review: bool
    native_observed: bool
    hard_gates: bool | None


def dataset(labels: tuple[BehaviorLabel, ...]) -> dict:
    if type(labels) is not tuple or any(type(x) is not BehaviorLabel for x in labels):
        raise ValueError('typed behavior labels required')
    seen = set()
    rows = []
    for x in labels:
        if (type(x.case_id) is not str or not x.case_id.strip() or x.case_id in seen
                or x.partition not in ('train', 'validation', 'held_out')
                or x.outcome not in ('pass', 'fail', 'unknown')
                or any(type(v) is not bool for v in (x.criteria_supported, x.independent_review, x.native_observed))
                or x.hard_gates is not None and type(x.hard_gates) is not bool):
            raise ValueError('invalid or duplicate behavior label')
        seen.add(x.case_id)
        reviewed = x.criteria_supported and x.independent_review and x.native_observed and x.outcome != 'unknown'
        rows.append({'case_id': x.case_id, 'partition': x.partition, 'outcome': x.outcome,
                     'status': 'golden_eligible' if reviewed else 'candidate',
                     'hard_gates': x.hard_gates,
                     'reward': (1 if x.outcome == 'pass' and x.hard_gates else 0)
                               if reviewed and x.hard_gates is not None else None})
    return {'cases': rows, 'evidence_ceiling': 'SUPPLIED_REVIEW_FACTS',
            'authorizes_training': False, 'authorizes_landing': False}


def paired_feedback(pair: PairInspection, baseline: tuple[BehaviorLabel, ...],
                    candidate: tuple[BehaviorLabel, ...]) -> dict:
    """Retain baseline on ties, unknowns and regressions. Cost never buys correctness."""
    if type(pair) is not PairInspection:
        raise ValueError('original pair inspection required')
    left, right = dataset(baseline), dataset(candidate)
    result = {'status': 'INCONCLUSIVE', 'recommendation': 'retain_baseline', 'reward_delta': None,
              'baseline': left, 'candidate': right, 'authorizes_adoption': False,
              'authorizes_training': False, 'authorizes_landing': False,
              'evidence_ceiling': pair.evidence_ceiling, 'reasons': []}
    if pair.status != 'STRUCTURALLY_COMPARABLE':
        result['reasons'] = list(pair.reasons) or ['pair_not_comparable']
        return result
    if not baseline or {x.case_id: x.partition for x in baseline} != {x.case_id: x.partition for x in candidate}:
        result['reasons'] = ['case_population_mismatch_or_empty']
        return result
    if any(x.partition == 'held_out' for x in (*baseline, *candidate)):
        result['reasons'] = ['held_out_must_not_drive_harness_selection']
        return result
    if any(x.hard_gates is False for x in candidate):
        result.update(status='REJECTED', reasons=['candidate_hard_gate_failure'])
        return result
    rows = left['cases'] + right['cases']
    if any(x['reward'] is None for x in rows):
        result['reasons'] = ['unreviewed_or_unknown_behavior']
        return result
    before = {x['case_id']: x['reward'] for x in left['cases']}
    deltas = [x['reward'] - before[x['case_id']] for x in right['cases']]
    result['reward_delta'] = sum(deltas) / len(deltas)
    if min(deltas) < 0:
        result.update(status='REJECTED', reasons=['protected_case_regression'])
    elif max(deltas) > 0:
        result.update(status='IMPROVEMENT_CANDIDATE', recommendation='outer_review_required',
                      reasons=['single_pair_not_repeated_transfer_evidence'])
    else:
        result.update(status='NOOP', reasons=['no_measured_improvement'])
    return result
