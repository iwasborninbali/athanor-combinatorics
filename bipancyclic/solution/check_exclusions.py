"""Independent stdlib-only checker for BPC1 exhaustive exclusion trees.

The checker does not import search code or read the search pattern files.
It generates every cyclic chord incidence pattern directly, enumerates kernel
cycles by vertex-simple walks, and checks each integer-simplex proof leaf.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import time


def diagrams(k):
    result = []
    for m in range(2, 2*k+1):
        representatives = set()
        edges = list(itertools.combinations(range(m), 2))
        for chords in itertools.combinations(edges, k):
            if set(itertools.chain.from_iterable(chords)) != set(range(m)):
                continue
            images = []
            for step in (-1, 1):
                for shift in range(m):
                    images.append(tuple(sorted(tuple(sorted(((step*u+shift) % m,
                                                              (step*v+shift) % m)))
                                               for u, v in chords)))
            representatives.add(min(images))
        for chords in sorted(representatives):
            result.append((m, chords))
    return result


def kernel_cycles(m, chords):
    """Enumerate cycles in the kernel multigraph by paths, not cycle space.

    Two parallel edges can be a kernel cycle: their expanded original-graph
    cycle has length >=4. Edge IDs distinguish the Hamilton arcs and chords.
    """
    edges = [(v, (v+1) % m) for v in range(m)] + list(chords)
    adj = [[] for _ in range(m)]
    for eid, (u, v) in enumerate(edges):
        adj[u].append((v, eid))
        adj[v].append((u, eid))
    found = set()
    for root in range(m):
        def walk(v, vertices, chosen):
            for w, eid in adj[v]:
                if eid in chosen:
                    continue
                if w == root:
                    if len(chosen) >= 1:
                        found.add(frozenset(chosen + (eid,)))
                elif w > root and w not in vertices:
                    walk(w, vertices | {w}, chosen + (eid,))
        walk(root, {root}, ())
    answer = []
    for cycle in found:
        arc_mask = sum(1 << i for i in cycle if i < m)
        chord_count = sum(i >= m for i in cycle)
        answer.append((arc_mask, chord_count))
    return sorted(answer)


def all_cases(n, k):
    patterns = diagrams(k)
    cases = []
    distribution = {}
    max_cycles = 0
    for pid, (m, chords) in enumerate(patterns):
        cycles = kernel_cycles(m, chords)
        max_cycles = max(max_cycles, len(cycles))
        distribution[m] = distribution.get(m, 0) + 1
        if len(cycles) < n//2-1:
            continue
        # The two colors may be globally interchanged, so fix color(0)=0.
        for coloring in range(1 << (m-1)):
            colors = [0] + [(coloring >> (i-1)) & 1 for i in range(1, m)]
            if any(colors[u] == colors[v] for u, v in chords):
                continue
            base = [1 if colors[i] != colors[(i+1) % m] else 2 for i in range(m)]
            # A chord between adjacent kernel vertices must not be a
            # Hamilton edge: the corresponding arc is odd and >=3.
            for i in range(m):
                if tuple(sorted((i, (i+1) % m))) in chords:
                    base[i] = 3
            left = n-sum(base)
            if left < 0:
                continue
            assert left % 2 == 0
            expressions = []
            for mask, chord_count in cycles:
                constant = chord_count + sum(base[i] for i in range(m) if mask >> i & 1)
                assert constant % 2 == 0
                expressions.append((mask, constant//2))
            cases.append((pid, coloring, m, left//2, expressions))
    return cases, distribution, max_cycles


def verify(path, verbose=False):
    before = time.monotonic()
    compressed = path.suffix == '.gz'
    raw = gzip.open(path, 'rb').read() if compressed else path.read_bytes()
    assert len(raw) >= 8 and raw[:4] == b'BPC1', 'bad magic/header'
    n, k, ncases = struct.unpack_from('<BBH', raw, 4)
    assert n >= 4 and n % 2 == 0 and 1 <= k <= 4
    cases, distribution, max_cycles = all_cases(n, k)
    assert ncases == len(cases), ('case coverage', ncases, len(cases))
    offset = 8
    total_nodes = total_assignments = 0
    records = []
    for pid, coloring, m, s, expressions in cases:
        assert offset+2 <= len(raw), 'missing case'
        assert raw[offset:offset+2] == bytes([pid, coloring]), 'case order/coverage'
        offset += 2
        masks = [a for a, b in expressions]
        values = [b for a, b in expressions]
        affects = [[j for j, mask in enumerate(masks) if mask >> i & 1] for i in range(m)]
        rest = [(1 << m) - (1 << d) for d in range(m)]
        partial_masks = [[mask & r for mask in masks] for r in rest]
        nodes = represented = 0

        def check_tree(depth, remaining):
            nonlocal offset, nodes, represented
            assert offset < len(raw), 'truncated proof'
            code = raw[offset]
            offset += 1
            nodes += 1
            if code:
                assert 2 <= code <= n//2, ('invalid target', code)
                # Every completion satisfies sum(remaining x_i)=remaining.
                # A 0/1 subset of those variables contributes exactly 0,
                # exactly remaining, or a value in [0,remaining].
                for value, mask in zip(values, partial_masks[depth]):
                    low = value + (remaining if mask == rest[depth] else 0)
                    high = low + (remaining if mask and mask != rest[depth] else 0)
                    assert not low <= code <= high, ('unsound leaf', pid, coloring, depth, code)
                represented += math.comb(remaining+m-depth-1, m-depth-1)
                return
            assert depth < m-1, 'branch after all free variables determined'
            for value in range(remaining+1):
                check_tree(depth+1, remaining-value)
                if value < remaining:
                    for j in affects[depth]:
                        values[j] += 1
            for j in affects[depth]:
                values[j] -= remaining

        check_tree(0, s)
        expected = math.comb(s+m-1, m-1)
        assert represented == expected, ('simplex accounting', pid, coloring)
        records.append({'pattern': pid, 'color': coloring, 'assignments': expected, 'nodes': nodes})
        total_nodes += nodes
        total_assignments += expected
        if verbose:
            print(f'checked N={n}, k={k}, pattern={pid}, color={coloring}, nodes={nodes}', flush=True)
    assert offset == len(raw), 'trailing data'
    result = {'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'N': n, 'k': k, 'patterns_by_endpoints': distribution, 'maximum_kernel_cycles': max_cycles,
              'cases': len(cases), 'assignments': total_assignments, 'nodes': total_nodes,
              'seconds': time.monotonic()-before, 'verdict': 'EXCLUSION VERIFIED', 'case_counts': records}
    print(json.dumps({a:b for a,b in result.items() if a != 'case_counts'}), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('proofs', type=Path, nargs='+')
    ap.add_argument('--output', type=Path)
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    results = [verify(p, args.verbose) for p in args.proofs]
    if args.output:
        args.output.write_text(json.dumps(results, indent=2)+'\n')


if __name__ == '__main__':
    main()
