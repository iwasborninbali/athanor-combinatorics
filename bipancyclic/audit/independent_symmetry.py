"""Check pattern counts with Burnside's lemma, not canonical representatives."""
import itertools
import json
from pathlib import Path
import time


def count(k, m):
    edges = list(itertools.combinations(range(m), 2))
    diagrams = []
    for chosen in itertools.combinations(edges, k):
        if set().union(*(set(e) for e in chosen)) == set(range(m)):
            diagrams.append(frozenset(chosen))
    counts = []
    for direction in (1, -1):
        for shift in range(m):
            fixed = 0
            for chosen in diagrams:
                image = frozenset(tuple(sorted(((direction*u+shift) % m,
                                                (direction*v+shift) % m)))
                                  for u, v in chosen)
                fixed += image == chosen
            counts.append(fixed)
    assert sum(counts) % (2*m) == 0
    assert sum(counts[:m]) % m == 0
    return dict(k=k, endpoints=m, labeled=len(diagrams),
                cyclic_orbits=sum(counts[:m])//m,
                dihedral_orbits=sum(counts)//(2*m),
                fixed_counts=counts)


if __name__ == "__main__":
    start=time.process_time()
    rows=[count(k,m) for k in (2,3,4) for m in range(2,2*k+1)]
    for row in rows: print(json.dumps(row))
    Path("independent_symmetry.json").write_text(json.dumps(dict(
        cpu_seconds=time.process_time()-start,results=rows),indent=2)+"\n")
