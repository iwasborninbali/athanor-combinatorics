#!/usr/bin/env python3
"""Independent stdlib check of one recorded matching obstruction."""
import argparse
import hashlib
import json
from pathlib import Path
from check_clique_proof import verify_hall_cut

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('catalogue')
ap.add_argument('state')
args = ap.parse_args()
source = Path(args.catalogue).read_bytes()
rows = [tuple(map(int, s.split())) for s in source.decode().splitlines() if s.strip()]
n, count = rows.pop(0)
assert count == len(rows)
raw = Path(args.state).read_bytes()
state = json.loads(raw)
assert state['order'] == n and state['target'] == n-1
indices = state['selected']+state['candidates']
assert len(indices) == len(set(indices)) and all(0 <= v < count for v in indices)
for v in indices:
    a = rows[v]
    assert len(a) == n and sorted(a) == list(range(n))
    assert len({(s-r, a[s]-a[r]) for r in range(n) for s in range(r+1, n)}) == n*(n-1)//2
result = verify_hall_cut(rows, state['selected'], state['candidates'], state['hall_rows_mask'], state['target'])
result.update(verified=True, catalogue_sha256=hashlib.sha256(source).hexdigest(),
              state_sha256=hashlib.sha256(raw).hexdigest(),
              scope='No target-size packing containing the selected arrays and using only the listed candidates for its remaining arrays.')
print(json.dumps(result, indent=2))
