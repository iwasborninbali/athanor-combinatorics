#!/usr/bin/env python3
"""Independent stdlib-only exhaustive clique decision audit.

This implementation uses arbitrary-precision integers for sets and a dynamic
row partition bound. It imports no search code or solver. If it finishes, it
exhaustively checks the requested nonexistence claim against the catalogue.
No symmetry reduction is used, including for pilots.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time


def audit(catalogue, target, seconds):
    source = Path(catalogue).read_bytes()
    rows = [tuple(map(int, s.split())) for s in source.decode().splitlines() if s.strip()]
    n, count = rows.pop(0)
    assert len(rows) == count == len(set(rows))
    full = (1 << count) - 1
    cells = [[0] * n for _ in range(n)]
    for i, a in enumerate(rows):
        assert len(a) == n and sorted(a) == list(range(n))
        # Independent validation via all pairs, including their row differences.
        v = [(s-r, a[s]-a[r]) for r in range(n) for s in range(r+1, n)]
        assert len(v) == len(set(v))
        for r, c in enumerate(a):
            cells[r][c] |= 1 << i
    adj = []
    for i, a in enumerate(rows):
        forbidden = 0
        for r, c in enumerate(a):
            forbidden |= cells[r][c]
        adj.append(full ^ forbidden)
    start = time.monotonic()
    calls = 0

    def visit(candidates, need):
        nonlocal calls
        calls += 1
        if calls % 4096 == 0 and time.monotonic() - start > seconds:
            raise TimeoutError
        if need == 0:
            return []
        if candidates.bit_count() < need:
            return None
        # Every clique meets each cell group of any one row at most once.
        if min(sum(bool(candidates & group) for group in row) for row in cells) < need:
            return None
        # Disjoint branching: every nonempty solution has a least index.
        while candidates.bit_count() >= need:
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            tail = visit(candidates & adj[i], need - 1)
            if tail is not None:
                return [i] + tail
        return None

    try:
        answer = visit(full, target)
        status = 'EXCLUDED' if answer is None else 'WITNESS'
    except TimeoutError:
        status, answer = 'TIMEOUT', None
    return {'status': status, 'order': n, 'target': target, 'calls': calls,
            'seconds': time.monotonic() - start, 'indices': answer,
            'catalogue_sha256': hashlib.sha256(source).hexdigest(),
            'scope': 'all catalogue arrays, no symmetry reduction'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('catalogue')
    ap.add_argument('target', type=int)
    ap.add_argument('--seconds', type=float, default=60)
    args = ap.parse_args()
    print(json.dumps(audit(args.catalogue, args.target, args.seconds), indent=2))
