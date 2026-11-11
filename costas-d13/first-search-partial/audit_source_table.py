"""Reproduce two printed-table errors without search software."""
import hashlib
import itertools
import json
from pathlib import Path

small = list(itertools.permutations(range(2)))
assert len(small) == 2 and all(small[0][r] != small[1][r] for r in range(2))
path = Path('data/costas_26.txt')
raw = path.read_bytes()
rows = [tuple(map(int, line.split())) for line in raw.decode().splitlines() if line.strip()]
assert rows.pop(0) == (26, 56) and len(rows) == 56 == len(set(rows))
for a in rows:
    assert sorted(a) == list(range(26))
    assert len({(j-i, a[j]-a[i]) for i in range(26) for j in range(i+1, 26)}) == 325
edges = sum(all(x != y for x, y in zip(a, b)) for i, a in enumerate(rows) for b in rows[:i])
record = {'source': 'Frank–Dinitz author manuscript dated 2013-01-28, Table 3.1, p. 6',
          'order2': {'printed_vertices': 1, 'actual_vertices': 2, 'actual_edges': 1},
          'order26': {'printed_edges': 6239, 'vertices': 56, 'maximum_possible_edges': 1540,
                      'rebuilt_edges': edges, 'catalogue_sha256': hashlib.sha256(raw).hexdigest()},
          'printed_values_visually_checked': 'sources/table31.png'}
Path('logs/source_table_audit.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
