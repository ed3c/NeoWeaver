#!/usr/bin/env python3
"""Non-interactive product operations, or the project-local MCP stdio transport."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neoweaver.product_cli import OPERATIONS, execute, operation_schemas, refused
from neoweaver.task_adapter import _json


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps(refused(message + '; Example: python3 scripts/neoweaver.py goal reconcile --stdin')),
              file=sys.stderr)
        self.exit(2)


def main(argv=None):
    parser = Parser(description=__doc__, epilog='Examples: python3 scripts/neoweaver.py goal reconcile --help')
    commands = parser.add_subparsers(dest='resource', required=True, parser_class=Parser)
    commands.add_parser('mcp', help='Serve MCP 2025-11-25 over stdio',
                        epilog='Examples: python3 scripts/neoweaver.py mcp')
    commands.add_parser('schema', help='Print the shared named operation schemas',
                        epilog='Examples: python3 scripts/neoweaver.py schema')
    for resource, verbs in {'goal': ('reconcile', 'refresh'), 'task': ('continue',), 'training': ('inspect',)}.items():
        group = commands.add_parser(resource, epilog=f'Examples: python3 scripts/neoweaver.py {resource} {verbs[0]} --help')
        subs = group.add_subparsers(dest='verb', required=True, parser_class=Parser)
        for verb in verbs:
            sub = subs.add_parser(verb, description=OPERATIONS[resource + '_' + verb][2],
                epilog=f'Examples: cat arguments.json | python3 scripts/neoweaver.py {resource} {verb} --stdin\n'
                       f'python3 scripts/neoweaver.py {resource} {verb} --input arguments.json')
            inputs = sub.add_mutually_exclusive_group(required=True)
            inputs.add_argument('--stdin', action='store_true', help='Read one strict JSON arguments object from stdin')
            inputs.add_argument('--input', type=Path, help='Read one strict JSON arguments object from a file')
            if resource == 'task':
                sub.add_argument('--dry-run', action='store_true', help='Return selected original next without calling carrier')
    args = parser.parse_args(argv)
    if args.resource == 'mcp':
        from neoweaver.mcp_stdio import serve
        return serve()
    if args.resource == 'schema':
        print(json.dumps(operation_schemas(), ensure_ascii=True, allow_nan=False))
        return 0
    try:
        payload = _json(sys.stdin.buffer.read() if args.stdin else args.input.read_bytes())
        if getattr(args, 'dry_run', False):
            if not isinstance(payload, dict):
                raise ValueError('arguments_object_required')
            payload['dry_run'] = True
        result = execute(args.resource + '_' + args.verb, payload)
    except KeyboardInterrupt:
        result = {'status': 'unknown', 'problem': 'interrupted_read_original_owner',
                  'authorizes_landing': False}
    except (OSError, ValueError, UnicodeError) as error:
        result = refused(error)
    error = result.get('status') in ('refused', 'failed', 'unknown', 'REFUSED', 'BLOCKED')
    print(json.dumps(result, ensure_ascii=True, allow_nan=False), file=sys.stderr if error else sys.stdout)
    return 2 if error else 0


if __name__ == '__main__':
    sys.exit(main())
