"""Original-graph simple-cycle audit; imports no submitted implementation."""
import collections
import hashlib
import json
from pathlib import Path
import time


def cycles(n, chords):
    ring = {tuple(sorted((v, (v + 1) % n))) for v in range(n)}
    edges = set(ring)
    for u, v in chords:
        assert 0 <= u < n and 0 <= v < n and u != v
        edge = tuple(sorted((u, v)))
        assert edge not in edges, ("repeated edge", edge)
        assert (u - v) % 2 == 1, ("not bipartite", edge)
        edges.add(edge)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    answer = []
    for root in range(n):
        path = [root]

        def visit(v, used):
            for w in adj[v]:
                if w == root:
                    if len(path) >= 3 and path[1] < path[-1]:
                        answer.append(path.copy())
                elif w > root and not (used >> w) & 1:
                    path.append(w)
                    visit(w, used | (1 << w))
                    path.pop()

        visit(root, 1 << root)
    # Independent explicit sequence checks, including uniqueness of edge sets.
    edge_sets = set()
    for cycle in answer:
        assert len(set(cycle)) == len(cycle)
        ec = frozenset(tuple(sorted((cycle[i-1], cycle[i])))
                       for i in range(len(cycle)))
        assert ec <= edges and ec not in edge_sets
        edge_sets.add(ec)
    return answer


if __name__ == "__main__":
    start = time.process_time()
    source = Path("../a03-bipancyclic/witnesses.json")
    rows = json.loads(source.read_text())
    assert sorted(row["N"] for row in rows) == list(range(4, 65, 2))
    results = []
    for row in rows:
        n, chords = row["N"], row["chords"]
        found = cycles(n, chords)
        histogram = collections.Counter(map(len, found))
        assert set(histogram) == set(range(4, n + 1, 2)), (n, histogram)
        results.append(dict(N=n, k=len(chords), total_cycles=len(found),
                            histogram=dict(sorted(histogram.items())), cycles=found))
        print(n, len(chords), len(found), dict(sorted(histogram.items())), flush=True)
    output = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  cpu_seconds=time.process_time()-start, results=results)
    Path("independent_witnesses.json").write_text(json.dumps(output, indent=2)+"\n")
