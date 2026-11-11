"""Extract a catalogue packing from a DIMACS SAT assignment; stdlib only."""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('catalogue')
ap.add_argument('solver_output')
ap.add_argument('witness')
args = ap.parse_args()
rows = [list(map(int, line.split())) for line in Path(args.catalogue).read_text().splitlines() if line.strip()]
n, count = rows.pop(0)
output = Path(args.solver_output).read_text()
assert 's SATISFIABLE' in output and 's UNSATISFIABLE' not in output
assignment = [int(w) for line in output.splitlines() if line.startswith('v ') for w in line.split()[1:]]
indices = sorted(x-1 for x in assignment if 1 <= x <= count)
assert len(indices) == n-1
obj = {'order': n, 'size': len(indices), 'index_base': 0,
       'catalogue_row_indices': indices, 'arrays': [rows[i] for i in indices]}
Path(args.witness).write_text(json.dumps(obj, indent=2)+'\n')
print(json.dumps({'witness': args.witness, 'order': n, 'size': len(indices)}))
