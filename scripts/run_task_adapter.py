"""Read or consume one original task continuation; never poll or self-approve."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neoweaver.task_adapter import PinnedLoopCLI, TaskAdapter, _json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selection', type=Path, help='Private selection with original request and carrier configuration')
    parser.add_argument('operation', choices=('inspect', 'advance'))
    parser.add_argument('capture', type=Path, help='Fresh external transport capture directory')
    parser.add_argument('--review', type=Path, help='Actual Session decision and original acceptance observation')
    args = parser.parse_args()
    try:
        selection = _json(args.selection.read_bytes())
        if not isinstance(selection, dict):
            raise ValueError('invalid_task_selection')
        if args.operation == 'inspect' and args.review:
            raise ValueError('inspect_cannot_submit_review')
        review = None
        if args.review:
            review = _json(args.review.read_bytes())
            if not isinstance(review, dict) or set(review) - {'decision', 'feedback', 'acceptance_review'}:
                raise ValueError('invalid_session_review')
        carrier = PinnedLoopCLI(selection['carrier'])
        adapter = TaskAdapter(selection['request'], carrier)
        if args.operation == 'inspect':
            state = adapter.inspect(args.capture)
        else:
            previous = adapter.readback(selection['readback'])
            state = adapter.advance(previous, args.capture, review=review)
        print(json.dumps(asdict(state), ensure_ascii=False, allow_nan=False))
        return 2 if state.status in ('unknown', 'refused', 'failed') else 0
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'status': 'refused', 'problem': str(error),
                          'authorizes_landing': False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
