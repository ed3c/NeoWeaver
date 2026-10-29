"""Emit one bounded, untrusted native-validation proposal; never execute it."""
import json
from pathlib import Path

from scripts.check_harness2 import pin


if __name__ == '__main__':
    print(json.dumps({'schema': 1, 'experiment': 'neoweaver-validation-k1',
                      'upstream': pin(Path(__file__).resolve().parents[1])}))
