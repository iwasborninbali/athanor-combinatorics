"""Four-chord diagrams and symbolic simple cycles (search implementation)."""
import json
from pathlib import Path
from itertools import combinations


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for j in range(1, len(vertices)):
        b = vertices[j]
        for rest in matchings(vertices[1:j] + vertices[j+1:]):
            yield ((a, b),) + rest


def canonical(pairs, m):
    return min(tuple(sorted(tuple(sorted(((s*a+r) % m, (s*b+r) % m)))
                            for a, b in pairs))
               for s in (1, -1) for r in range(m))


def cycles(pairs, m=None):
    if m is None:
        m = 2*len(pairs)
    edges = [(i, (i+1) % m) for i in range(m)] + list(pairs)
    found = []
    # Select chords. The vertex degree parity equations determine circle edges
    # after the last circle edge is chosen, giving exactly two possibilities.
    for chosen in range(1 << len(pairs)):
        endpoint = [0]*m
        for j, (a, b) in enumerate(pairs):
            if chosen >> j & 1:
                endpoint[a] ^= 1
                endpoint[b] ^= 1
        for last in (0, 1):
            arc = []
            prev = last
            for parity in endpoint:
                prev ^= parity
                arc.append(prev)
            assert arc[-1] == last
            ids = [i for i, value in enumerate(arc) if value]
            ids += [m+j for j in range(len(pairs)) if chosen >> j & 1]
            if not ids:
                continue
            adj = [[] for _ in range(m)]
            for j in ids:
                a, b = edges[j]
                adj[a].append(b)
                adj[b].append(a)
            if any(len(v) not in (0, 2) for v in adj):
                continue
            seen = set()
            stack = [edges[ids[0]][0]]
            while stack:
                v = stack.pop()
                if v not in seen:
                    seen.add(v)
                    stack.extend(adj[v])
            if len(seen) == sum(bool(v) for v in adj):
                found.append({'arcs': [i for i in range(m) if arc[i]],
                              'chords': chosen.bit_count(), 'chord_mask': chosen})
    return found


def build(k):
    m = 2*k
    reps = sorted({canonical(p, m) for p in matchings(tuple(range(m)))})
    return [{'id': i, 'pairs': p, 'cycles': cycles(p)} for i, p in enumerate(reps)]


def build_all(k):
    """All endpoint-sharing patterns, with strictly positive circle arcs.

    Choose exactly k distinct chords on m occupied endpoints, where m<=2k.
    Cyclic endpoint labels are reduced only by rotations and reflection.
    """
    out = []
    for m in range(2, 2*k+1):
        reps = set()
        for pairs in combinations(list(combinations(range(m), 2)), k):
            if len({v for e in pairs for v in e}) == m:
                reps.add(canonical(pairs, m))
        for pairs in sorted(reps):
            out.append({'id': len(out), 'm': m, 'pairs': pairs,
                        'cycles': cycles(pairs, m)})
    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--chords', type=int, default=4)
    ap.add_argument('--out', default='patterns4.json')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    data = build_all(args.chords) if args.all else build(args.chords)
    Path(args.out).write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'patterns': len(data), 'cycle_counts': [len(p['cycles']) for p in data]}))
