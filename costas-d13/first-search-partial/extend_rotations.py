"""Try to extend two mutually disjoint four-rotation groups to 11 or 12.

This construction search has no bearing on general nonexistence.
"""
import itertools
import json
from pathlib import Path
import time

start = time.monotonic()
n = 13
lines = [tuple(map(int, s.split())) for s in Path('data/costas_13.txt').read_text().splitlines() if s.strip()]
assert lines.pop(0) == (13, 12828)
masks = [sum(1 << (r*n+c) for r, c in enumerate(a)) for a in lines]
lookup = {mask: i for i, mask in enumerate(masks)}
groups = set()
for a in lines:
    pts = list(enumerate(a))
    orbit = []
    for _ in range(4):
        orbit.append(sum(1 << (r*n+c) for r, c in pts))
        pts = [(c, n-1-r) for r, c in pts]
    if len(set(orbit)) == 4 and all(x & y == 0 for x, y in itertools.combinations(orbit, 2)):
        groups.add(tuple(sorted(orbit)))
groups = sorted(groups)
unions = [g[0] | g[1] | g[2] | g[3] for g in groups]
pairs, max_candidates, found11, found12 = 0, 0, False, False

def complete(candidates, need):
    if len(candidates) < need:
        return None
    if need == 0:
        return []
    for position, v in enumerate(candidates):
        if len(candidates)-position < need:
            break
        tail = complete([w for w in candidates[position+1:] if not masks[v] & masks[w]], need-1)
        if tail is not None:
            return [v]+tail
    return None

def save(indices):
    size = len(indices)
    obj = {'order': n, 'size': size, 'index_base': 0,
           'catalogue_row_indices': indices, 'arrays': [lines[i] for i in indices]}
    Path(f'certificates/extended_rotations_13_{size}.json').write_text(json.dumps(obj, indent=2)+'\n')

for i in range(len(groups)):
    for j in range(i):
        if unions[i] & unions[j]:
            continue
        pairs += 1
        occupied = unions[i] | unions[j]
        candidates = [v for v, mask in enumerate(masks) if not mask & occupied]
        max_candidates = max(max_candidates, len(candidates))
        base = [lookup[x] for g in (groups[i], groups[j]) for x in g]
        tail = complete(candidates, 4)
        if tail is not None:
            found12 = True
            save(base+tail)
            break
        if not found11:
            tail = complete(candidates, 3)
            if tail is not None:
                found11 = True
                save(base+tail)
    if found12:
        break
result = {'four_rotation_groups': len(groups), 'pairs_examined': pairs,
          'max_extension_candidates': max_candidates,
          'found11': found11, 'found12': found12,
          'seconds': time.monotonic()-start,
          'scope': 'extensions of two four-rotation orbits at order 13'}
Path('logs/extend_rotations_13.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
