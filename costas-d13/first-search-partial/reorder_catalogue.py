"""Reorder the unchanged catalogue by disjointness degree for discovery."""
import hashlib
import json
from pathlib import Path

n = 13
source = Path('data/costas_13.txt')
rows = [tuple(map(int, s.split())) for s in source.read_text().splitlines() if s.strip()]
order, count = rows.pop(0)
assert order == n and len(rows) == count
cells = [[0]*n for _ in range(n)]
for i, a in enumerate(rows):
    for r, c in enumerate(a):
        cells[r][c] |= 1 << i
degree = []
for a in rows:
    excluded = 0
    for r, c in enumerate(a):
        excluded |= cells[r][c]
    degree.append(count-excluded.bit_count())
indices = sorted(range(count), key=lambda i: (-degree[i], rows[i]))
out = Path('data/costas_13_degree.txt')
out.write_text(f'{n} {count}\n'+''.join(' '.join(map(str, rows[i]))+'\n' for i in indices))
record = {'order': n, 'vertices': count, 'degree_min': min(degree),
          'degree_max': max(degree), 'edges': sum(degree)//2,
          'original_row_indices': indices,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'reordered_sha256': hashlib.sha256(out.read_bytes()).hexdigest()}
Path('data/costas_13_degree.meta.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k != 'original_row_indices'}))
