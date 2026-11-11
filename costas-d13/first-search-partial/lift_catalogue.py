"""Generate a restricted construction family by augmenting order-12 arrays.

For a 13-array avoiding the bottom-right corner, delete the last row/column
and join the two severed dots. Keep it when the resulting 12-permutation is
itself a Costas array. Exclusion in this family is not general exclusion.
"""
import json
from pathlib import Path

def read(n):
    rows = [tuple(map(int, s.split())) for s in Path(f'data/costas_{n}.txt').read_text().splitlines() if s.strip()]
    assert rows.pop(0)[0] == n
    return rows

small = set(read(12))
large = read(13)
keep = []
for a in large:
    if a[-1] == 12:
        continue
    oldrow = a.index(12)
    b = list(a[:-1])
    b[oldrow] = a[-1]
    if tuple(b) in small:
        keep.append(a)
out = Path('data/liftable_13.txt')
out.write_text(f'13 {len(keep)}\n'+''.join(' '.join(map(str, a))+'\n' for a in keep))
Path('logs/lift_catalogue.json').write_text(json.dumps({'order': 13, 'restricted_arrays': len(keep), 'scope': 'bottom-right-hole augmentation of an order-12 Costas Latin square'}, indent=2)+'\n')
print(len(keep))
