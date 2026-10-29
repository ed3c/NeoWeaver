#!/usr/bin/env python3
"""Check complete vendor bytes against the original Git blob inventory."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

from check_compiled_contracts import load, require


def check(root):
    root = root.resolve()
    vendor = root / 'third_party/harness2'
    source = load(root / 'third_party/harness2.source.json')
    require(isinstance(source, dict) and set(source) == {'repository', 'revision', 'tree', 'files'},
            'invalid_upstream_inventory')
    require(not vendor.is_symlink() and not vendor.parent.is_symlink(), 'upstream_symlink')
    expected = source['files']
    require(isinstance(expected, dict) and expected, 'empty_upstream_inventory')
    actual = set()
    for path in vendor.rglob('*'):
        relative = path.relative_to(vendor)
        require(not path.is_symlink(), 'upstream_symlink')
        if '__pycache__' in relative.parts or 'harness2.egg-info' in relative.parts:
            continue
        if path.is_file():
            actual.add(relative.as_posix())
    require(actual == set(expected), 'upstream_file_inventory_changed')
    for name, blob in expected.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts
                and path.as_posix() == name and '\\' not in name, 'unsafe_upstream_path')
        file = vendor / name
        require(file.stat().st_mode & 0o111 == 0, 'upstream_mode_changed:' + name)
        raw = file.read_bytes()
        observed = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(observed == blob, 'upstream_bytes_changed:' + name)
    return {'valid': True, 'revision': source['revision'], 'files': len(expected),
            'proof_ceiling': 'DECLARED_UPSTREAM_BYTES_ONLY', 'effects': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root)))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
