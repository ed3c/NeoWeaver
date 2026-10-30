"""Scratch-only code mutations. Requires Python; never edits original task data."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
CASES = [
    ('local_task_closes_whole', 'neoweaver/product_goal.py', "'whole_goal': 'OPEN'", "'whole_goal': 'CLOSED'",
     'test_product_goal.ProductGoalTests.test_original_full_goal_and_cards_survive_local_completion'),
    ('capture_retry_replays', 'neoweaver/product_cli.py', "    except FileExistsError:\n        return {'status': 'unknown'",
     "    except FileExistsError:\n        adapter._call(previous.action['tool'], previous.action['arguments'], root / 'unsafe-replay')\n        return {'status': 'unknown'",
     'test_product_cli.ProductCLITests.test_dry_run_and_resend_do_not_duplicate_effect'),
    ('mutate_original_request', 'neoweaver/product_cli.py', '    previous = adapter.readback(selected[\'readback\'])',
     '    Path(selected[\'request\'][\'path\']).write_text(\'{}\')\n    previous = adapter.readback(selected[\'readback\'])',
     'test_product_cli.ProductCLITests.test_mechanical_chain_reaches_original_acceptance_without_new_ledger'),
]


def run(root, test):
    return subprocess.run([sys.executable, '-B', '-m', 'unittest', test], cwd=root,
                          env={**os.environ, 'PYTHONPATH': str(root) + os.pathsep + str(root / 'tests')},
                          capture_output=True, text=True, timeout=60)


def main():
    for name, relative, old, new, test in CASES:
        baseline = run(ROOT, test)
        if baseline.returncode:
            print(name, 'BASELINE_FAILED', baseline.stdout, baseline.stderr)
            return 1
        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary)
            for directory in ('neoweaver', 'scripts', 'tests', 'docs/specs', 'docs/compiled'):
                shutil.copytree(ROOT / directory, scratch / directory)
            target = scratch / relative
            source = target.read_text()
            if old not in source:
                raise RuntimeError('mutation_target_changed:' + name)
            position = source.rfind(old)
            target.write_text(source[:position] + new + source[position + len(old):])
            mutant = run(scratch, test)
            print(name, 'CAUGHT' if mutant.returncode else 'MISSED')
            print(mutant.stdout, mutant.stderr)
            if mutant.returncode == 0:
                return 1
        restored = run(ROOT, test)
        if restored.returncode:
            print(name, 'RESTORE_CHECK_FAILED', restored.stdout, restored.stderr)
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
