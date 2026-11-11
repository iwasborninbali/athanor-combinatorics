"""Finite search over disjoint four-rotation orbits; not a general exclusion."""
import itertools
import json
from pathlib import Path
import time


def run(n):
    started = time.monotonic()
    words = list(map(int, Path(f'data/costas_{n}.txt').read_text().split()))
    count = words[1]
    arrays = [tuple(words[2+i*n:2+(i+1)*n]) for i in range(count)]
    lookup = {a: i for i, a in enumerate(arrays)}
    groups = {}
    for a in arrays:
        points = list(enumerate(a))
        masks = []
        for _ in range(4):
            masks.append(sum(1 << (r*n+c) for r, c in points))
            points = [(c, n-1-r) for r, c in points]
        if len(set(masks)) == 4 and all(x & y == 0 for x, y in itertools.combinations(masks, 2)):
            groups.setdefault(tuple(sorted(masks)), None)
    groups = list(groups)
    unions = [x[0] | x[1] | x[2] | x[3] for x in groups]
    adjacency = [set() for _ in groups]
    for i, u in enumerate(unions):
        for j in range(i):
            if not u & unions[j]:
                adjacency[i].add(j)
                adjacency[j].add(i)
    triple = next(((i, j, k) for i in range(len(groups))
                   for j in sorted(adjacency[i]) if j < i
                   for k in sorted(adjacency[i] & adjacency[j]) if k < j), None)
    result = {'order': n, 'four_rotation_groups': len(groups),
              'group_graph_edges': sum(map(len, adjacency)) // 2,
              'triple': triple, 'seconds': time.monotonic()-started,
              'scope': 'three disjoint four-rotation orbits only'}
    if triple:
        ans = [[next(c for c in range(n) if mask >> (r*n+c) & 1) for r in range(n)]
               for x in triple for mask in groups[x]]
        witness = {'order': n, 'size': len(ans), 'index_base': 0,
                   'arrays': ans, 'catalogue_row_indices': [lookup[tuple(a)] for a in ans]}
        wp = Path(f'certificates/rotation_witness_{n}_{len(ans)}.json')
        wp.write_text(json.dumps(witness, indent=2)+'\n')
        result['witness'] = str(wp)
    Path(f'logs/symmetry_{n}.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    import sys
    for n in map(int, sys.argv[1:]):
        run(n)
