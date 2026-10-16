#!/usr/bin/env python3
"""Forward this repository's semantic request to the original Soodles owner."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_request_field:' + key)
        result[key] = value
    return result


def enter(request_file, soodles='soodles', repository=ROOT):
    path = Path(request_file).resolve(strict=True)
    request = json.loads(path.read_bytes(), object_pairs_hook=unique_fields)
    if (not isinstance(request, dict)
            or type(request.get('schema')) is not int
            or request['schema'] != 1):
        raise ValueError('unsupported_loop_request_schema')
    selected_repository = request.get('repository')
    if not isinstance(selected_repository, str) or not Path(selected_repository).is_absolute():
        raise ValueError('loop_request_requires_absolute_repository')
    if Path(selected_repository).resolve(strict=True) != repository.resolve():
        raise ValueError('loop_request_repository_mismatch')
    return subprocess.run(
        [soodles, 'loop', 'enter', '--request-file', str(path)],
        cwd=repository, check=False,
    ).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-file', required=True, type=Path)
    parser.add_argument('--soodles', default='soodles', help='Installed Soodles executable or explicit owner path')
    args = parser.parse_args(argv)
    try:
        return enter(args.request_file, args.soodles)
    except (OSError, ValueError) as error:
        print(json.dumps({'status': 'REFUSED', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
