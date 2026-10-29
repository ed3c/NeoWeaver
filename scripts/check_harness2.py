#!/usr/bin/env python3
"""Verify an intact upstream checkout and run only its credential-free demo."""
import argparse
from importlib.metadata import PackageNotFoundError, distribution
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import sysconfig
import tomllib


def pin(root):
    requirement = (root / 'requirements-harness2.txt').read_text(encoding='utf-8')
    matches = re.findall(
        r'^harness2 @ git\+https://github\.com/google-research/harness2\.git@([0-9a-f]{40})$',
        requirement, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('one exact Google Harness2 source pin required')
    return matches[0]


def git(source, *args, input=None):
    return subprocess.run(['git', '-C', str(source), *args], input=input,
                          capture_output=True, check=True).stdout


def check_source(source, expected):
    source = source.resolve(strict=True)
    if git(source, 'rev-parse', '--show-toplevel').decode().strip() != str(source):
        raise ValueError('source must be an exact Git checkout root')
    if git(source, 'rev-parse', 'HEAD').decode().strip() != expected:
        raise ValueError('upstream HEAD differs from the selected pin')
    entries = git(source, 'ls-tree', '-r', '-z', 'HEAD').split(b'\0')
    count = 0
    for entry in filter(None, entries):
        metadata, raw_path = entry.split(b'\t', 1)
        mode, kind, expected_blob = metadata.split()
        name = os.fsdecode(raw_path)
        path = source / name
        if kind != b'blob':
            raise ValueError('unsupported upstream entry: ' + name)
        if mode == b'120000':
            if not path.is_symlink():
                raise ValueError('upstream symlink changed: ' + name)
            raw = os.fsencode(os.readlink(path))
        else:
            if path.is_symlink() or not path.is_file():
                raise ValueError('upstream file missing or aliased: ' + name)
            if bool(path.stat().st_mode & 0o111) != (mode == b'100755'):
                raise ValueError('upstream executable mode changed: ' + name)
            raw = path.read_bytes()
        actual_blob = git(source, 'hash-object', '--stdin', input=raw).strip()
        if actual_blob != expected_blob:
            raise ValueError('upstream bytes changed: ' + name)
        count += 1
    if git(source, 'ls-files', '--others', '--exclude-standard').strip():
        raise ValueError('untracked files in the upstream checkout')
    return count


def verify(source, output, expected):
    count = check_source(source, expected)
    source = source.resolve()
    output = output.resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('demo output must be separate from the upstream checkout')
    if output.exists():
        raise ValueError('fresh demo output required; preserve prior evidence')
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
           'PYTHONPATH': str(source)}
    subprocess.run([sys.executable, '-m', 'harness2.cli.demo', '--mode', 'both',
                    '--k', '2', '--output', str(output)], cwd=source,
                   env=env, check=True)
    report = json.loads((output / 'demo.json').read_text(encoding='utf-8'))
    if (report['done'], report['failed']) != (2, 0):
        raise ValueError('upstream demo did not complete both tasks')
    for task in ('ledger-1', 'ledger-2'):
        summary = json.loads((output / 'runs/demo-oc-agg2' / task / 'summary.json').read_text())
        expected_answer = 'Total: 85.15\n' if task == 'ledger-1' else 'Total: 20.25\n'
        for mode in ('agg', 'seq'):
            chosen = Path(summary['selections'][mode]['chosen_run_dir'])
            if (chosen / 'answer.txt').read_text() != expected_answer:
                raise ValueError('demo answer mismatch: ' + task + '/' + mode)
    scripts = tomllib.loads((source / 'pyproject.toml').read_text())['project']['scripts']
    installed = distribution('harness2')
    origin = json.loads(installed.read_text('direct_url.json') or '{}')
    if origin.get('vcs_info', {}).get('commit_id') != expected:
        raise ValueError('installed package is not bound to the selected Git pin')
    entries = {entry.name: entry.value for entry in installed.entry_points
               if entry.group == 'console_scripts'}
    if entries != scripts:
        raise ValueError('installed original CLI inventory differs from upstream')
    for name, entry in scripts.items():
        module = entry.split(':')[0]
        if not (source / (module.replace('.', '/') + '.py')).is_file():
            raise ValueError('original CLI module missing: ' + name)
        subprocess.run([str(Path(sysconfig.get_path('scripts')) / name), '--help'], cwd=source,
                       env=env, check=True, stdout=subprocess.DEVNULL)
    if check_source(source, expected) != count:
        raise ValueError('upstream inventory changed during verification')
    return {'upstream': expected, 'tracked_files': count, 'cli_help': sorted(scripts),
            'demo_modes': ['parallel', 'sequential'], 'tasks': report['done'],
            'evidence_ceiling': 'CREDENTIAL_FREE_DETERMINISTIC_DEMO',
            'subscription_native': 'NOT_RUN', 'authorizes_promotion': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.source, args.output, pin(Path(__file__).resolve().parents[1]))
    except (ValueError, OSError, PackageNotFoundError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'refused', 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
