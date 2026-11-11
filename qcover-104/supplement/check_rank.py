#!/usr/bin/env python3
"""Second independent stdlib-only audit, by Gaussian rank tests alone.

No search imports or incidence data. Each of the 1953 unordered pairs of
distinct nonzero vectors is tested for containment in at least one block.
Over F_2 these pairs represent all 651 two-spaces, three pairs per space.
"""
import argparse
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path


def gaussian_rank(rows, n):
    work = list(rows)
    used = 0
    for col in reversed(range(n)):
        pivot = None
        for j in range(used, len(work)):
            if work[j] & (1 << col):
                pivot = j
                break
        if pivot is None:
            continue
        work[used], work[pivot] = work[pivot], work[used]
        for j in range(used + 1, len(work)):
            if work[j] & (1 << col):
                work[j] ^= work[used]
        used += 1
    return used


def audit(path, maximum):
    raw = Path(path).read_bytes()
    w = json.loads(raw)
    assert [w['n'], w['k'], w['r']] == [6, 3, 2]
    blocks = w['basis_rows']
    assert len(blocks) <= maximum
    for b in blocks:
        assert len(b) == 3
        assert all(type(v) is int and 1 <= v <= 63 for v in b)
        assert gaussian_rank(b, 6) == 3
    for a, b in combinations(blocks, 2):
        assert gaussian_rank(a + b, 6) > 3, 'duplicate subspace'
    counts = {}
    witnesses = {}
    pairs = 0
    for x, y in combinations(range(1, 64), 2):
        line = tuple(sorted((x, y, x ^ y)))
        containing = [j for j, b in enumerate(blocks)
                      if gaussian_rank(b + [x, y], 6) == 3]
        assert containing, ('uncovered pair', x, y)
        if line in counts:
            assert counts[line] == len(containing)
        counts[line] = len(containing)
        witnesses[line] = containing
        pairs += 1
    assert pairs == 1953 and len(counts) == 651
    assert sum(counts.values()) == 7 * len(blocks)
    private = [0] * len(blocks)
    for js in witnesses.values():
        if len(js) == 1:
            private[js[0]] += 1
    result = {'sha256': hashlib.sha256(raw).hexdigest(), 'blocks': len(blocks),
              'pairs_checked': pairs, 'two_spaces_checked': len(counts),
              'multiplicity_histogram': dict(sorted(Counter(counts.values()).items())),
              'private_two_spaces_per_block': dict(sorted(Counter(private).items())),
              'verified_by_gaussian_rank': True}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('witness')
    p.add_argument('--max', type=int, default=104)
    args = p.parse_args()
    audit(args.witness, args.max)
