#!/usr/bin/env python3
"""Independent stdlib-only witness checker. Does not import search software.

Coordinates are zero based: a[r] is the column of the dot in row r.
The displacement check enumerates all pairs directly, rather than using
the difference-triangle predicate used in catalogue validation.
"""
import argparse
import hashlib
import json
from pathlib import Path


def check(witness, catalogue=None):
    raw = Path(witness).read_bytes()
    obj = json.loads(raw)
    n, k = obj['order'], obj['size']
    assert type(n) is int and n > 0
    assert type(k) is int and 0 < k <= n
    assert obj['index_base'] == 0
    arrays = obj['arrays']
    assert len(arrays) == k
    occupied = set()
    for index, a in enumerate(arrays):
        assert len(a) == n and all(type(x) is int for x in a)
        assert sorted(a) == list(range(n)), ('not a permutation', index)
        vectors = set()
        for r in range(n):
            cell = r, a[r]
            assert cell not in occupied, ('shared cell', index, cell)
            occupied.add(cell)
            for s in range(r + 1, n):
                vector = s - r, a[s] - a[r]
                assert vector not in vectors, ('repeated displacement', index, vector)
                vectors.add(vector)
        assert len(vectors) == n * (n - 1) // 2
    result = {'verified': True, 'order': n, 'size': k,
              'occupied_cells': len(occupied),
              'witness_sha256': hashlib.sha256(raw).hexdigest()}
    if catalogue:
        source = Path(catalogue).read_bytes()
        rows = [tuple(map(int, s.split())) for s in source.decode().splitlines() if s.strip()]
        assert rows[0][0] == n and len(rows) - 1 == rows[0][1]
        assert len(set(rows[1:])) == len(rows) - 1
        indices = obj['catalogue_row_indices']
        assert len(indices) == k
        for a, i in zip(arrays, indices):
            assert 0 <= i < len(rows) - 1 and tuple(a) == rows[i + 1]
        result['catalogue_sha256'] = hashlib.sha256(source).hexdigest()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('witness')
    parser.add_argument('--catalogue')
    args = parser.parse_args()
    print(json.dumps(check(args.witness, args.catalogue), indent=2))
