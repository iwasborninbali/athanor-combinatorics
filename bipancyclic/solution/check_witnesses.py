"""Independent stdlib-only verifier: enumerate cycles in the original graph.

This file deliberately does not import any search or symbolic pattern code.
Usage: python3 check_witnesses.py witnesses.json
"""
import argparse
import hashlib
import json
from pathlib import Path


def enumerate_cycles(n, chords):
    assert n >= 4 and n % 2 == 0
    edges = {tuple(sorted((i, (i + 1) % n))) for i in range(n)}
    for edge in chords:
        assert len(edge) == 2
        a, b = edge
        assert isinstance(a, int) and isinstance(b, int)
        assert 0 <= a < n and 0 <= b < n and (a-b) % 2
        pair = tuple(sorted((a, b)))
        assert pair not in edges, ('duplicate or Hamilton edge', edge)
        edges.add(pair)
    adjacency = [[] for _ in range(n)]
    for a, b in sorted(edges):
        adjacency[a].append(b)
        adjacency[b].append(a)
    counts = {}
    examples = {}
    # A cycle is visited from its least vertex, in its two orientations.
    # Keep the orientation in which the second vertex is below the last.
    for start in range(n):
        path = [start]
        def walk(v, visited):
            for w in adjacency[v]:
                if w == start:
                    if len(path) >= 3 and path[1] < path[-1]:
                        length = len(path)
                        counts[length] = counts.get(length, 0) + 1
                        examples.setdefault(length, path.copy())
                elif w > start and not (visited >> w & 1):
                    path.append(w)
                    walk(w, visited | (1 << w))
                    path.pop()
        walk(start, 1 << start)
    return counts, examples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?', default='witnesses.json')
    ap.add_argument('--output')
    args = ap.parse_args()
    raw = Path(args.file).read_bytes()
    data = json.loads(raw)
    results = []
    for item in data:
        n, chords = item['N'], item['chords']
        counts, examples = enumerate_cycles(n, chords)
        assert set(counts) == set(range(4, n+1, 2)), (n, sorted(counts))
        results.append({'N': n, 'chords': chords, 'k': len(chords),
                        'cycle_counts': counts, 'one_cycle_per_length': examples})
        print(f'N={n}: {len(chords)} chords, {sum(counts.values())} simple cycles, all even lengths present')
    output = {'checker': 'original-graph depth-first enumeration',
              'witness_sha256': hashlib.sha256(raw).hexdigest(), 'results': results}
    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2)+'\n')


if __name__ == '__main__':
    main()
