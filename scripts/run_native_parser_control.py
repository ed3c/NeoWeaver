"""Exercise the two native APIs once per H0 arm using an Owner's pinned task."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neoweaver.native import DecisionOracle, FixedConditions, NativeTask, inspect_native_pair, run_native_arm
from neoweaver.snapshot import materialize_source_pair


def read_pinned(reference):
    data = Path(reference['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != reference['sha256']:
        raise ValueError('selected input changed: ' + reference['path'])
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selection', type=Path, help='Original task JSON with selected_native_task')
    parser.add_argument('source_head', help='Exact clean source HEAD to stage unchanged in both arms')
    args = parser.parse_args()
    selection = json.loads(args.selection.read_bytes())['selected_native_task']
    root = Path(selection['evidence_root']).absolute()
    if root.exists() or root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError('evidence root must be fresh and outside source')
    root = root.resolve(strict=False)
    repository = Path(__file__).resolve().parents[1]
    if root == repository or repository in root.parents or root in repository.parents:
        raise ValueError('evidence root overlaps repository')
    read_pinned(selection['cli'])
    prompt, schema, population, expected = (read_pinned(selection[key]) for key in (
        'prompt', 'schema', 'population', 'oracle_verification_only'))
    if str(selection['oracle_verification_only']['path']).encode() in prompt or expected in prompt:
        raise ValueError('verification Oracle appears in prompt')
    task = NativeTask(Path(selection['cli']['path']), selection['model'], selection['effort'],
                      prompt, schema, population, selection['timeout_seconds'], selection['seed_policy'])
    oracle = DecisionOracle(task, expected)
    conditions = FixedConditions()
    root.mkdir(mode=0o700)
    (root / 'selection.json').write_bytes(args.selection.read_bytes())
    (root / 'oracle.json').write_bytes(expected)
    pair = materialize_source_pair(repository, args.source_head, root / 'source')
    captures = []
    for arm in ('baseline', 'candidate'):
        capture = run_native_arm(pair, arm, task, conditions, root / arm)
        captures.append(capture)
        print(json.dumps({'arm':arm, 'exit_code':capture.exit_code, 'timed_out':capture.timed_out,
                          'source_error':capture.source_error}), flush=True)
    for key in ('cli', 'prompt', 'schema', 'population', 'oracle_verification_only'):
        read_pinned(selection[key])
    if (root / 'oracle.json').read_bytes() != expected:
        raise ValueError('frozen verification Oracle changed')
    report = inspect_native_pair(*captures, oracle)
    summary = {
        'source_commit':pair.commit, 'source_tree':pair.tree,
        'treatment':report.treatment, 'launch_mismatches':report.launch_mismatches,
        'oracle_results':[dict(status=r.status, reasons=r.reasons, completed=r.completed,
                               thread_id=r.thread_id, terminal=r.terminal, usage=dict(r.usage))
                          for r in report.oracle_results],
        'pair':asdict(report.pair),
        'isolation_verified':False, 'effect_status':'unknown',
        'scope':'SOURCE_ASSISTED_VALIDATION_ONLY', 'authorizes_training':False,
        'authorizes_landing':False,
    }
    (root / 'report.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
