#!/usr/bin/env python3
"""Independent stdlib certificate audit, using integer sets of catalogue rows.
No search source is imported. Accepts only the three production trace opcodes.
A scoped audit requires ENDROOTS and explicitly reports its root ordinals.
"""
import argparse
import gzip
import hashlib
import json
import time
from pathlib import Path


def audit(catalogue, proof, target, root_ordinals=None):
    started = time.monotonic()
    raw = Path(catalogue).read_bytes()
    rows = [list(map(int, line.split())) for line in raw.splitlines() if line.strip()]
    n, m = rows.pop(0)
    assert len(rows) == m and len({tuple(x) for x in rows}) == m
    for a in rows:
        assert sorted(a) == list(range(n))
        for distance in range(1, n):
            differences = [a[r + distance] - a[r] for r in range(n - distance)]
            assert len(set(differences)) == len(differences)
    index = {tuple(a): v for v, a in enumerate(rows)}
    rep = []
    for a in rows:
        orbit = []
        for transpose in (False, True):
            for flip_r in (False, True):
                for flip_c in (False, True):
                    image = [-1] * n
                    for r, c in enumerate(a):
                        u, v = (c, r) if transpose else (r, c)
                        if flip_r:
                            u = n - 1 - u
                        if flip_c:
                            v = n - 1 - v
                        image[u] = v
                    orbit.append(index[tuple(image)])
        rep.append(min(orbit))
    incidence = [[0] * n for _ in range(n)]
    for v, a in enumerate(rows):
        for r, c in enumerate(a):
            incidence[r][c] |= 1 << v
    full = (1 << m) - 1
    adjacency = []
    for a in rows:
        conflict = 0
        for r, c in enumerate(a):
            conflict |= incidence[r][c]
        adjacency.append(full ^ conflict)
    nodes = 0
    roots = []
    stream = gzip.open(proof, 'rb')

    def visit(p, need):
        nonlocal nodes
        assert need > 0, 'a target clique exists'
        nodes += 1
        byte = stream.read(1)
        assert len(byte) == 1, 'truncated proof'
        op = byte[0]
        if op == 253:
            assert p.bit_count() < need, 'false cardinality bound'
            return
        if op < 2 * n:
            r = op if op < n else op - n
            groups = [(p & (incidence[r][c] if op < n else incidence[c][r])) for c in range(n)]
            groups = [g for g in groups if g]
            groups.sort(key=lambda g: (-g.bit_count(), (g & -g).bit_length()))
        else:
            assert op == 254, ('unknown opcode', op)
            groups = []
            uncoloured = p
            while uncoloured:
                available = uncoloured
                group = 0
                while available:
                    bit = available & -available
                    v = bit.bit_length() - 1
                    group |= bit
                    uncoloured ^= bit
                    available &= ~(adjacency[v] | bit)
                groups.append(group)
        # These are reconstructed partitions; no branch or bound is trusted.
        assert sum(g.bit_count() for g in groups) == p.bit_count()
        active = p
        for j in range(len(groups) - 1, need - 2, -1):
            group = groups[j]
            while group:
                assert need > 1, 'certificate skips a target clique'
                v = group.bit_length() - 1
                bit = 1 << v
                assert active & bit
                visit(active & adjacency[v], need - 1)
                active ^= bit
                group ^= bit

    ordinal = -1
    for v in range(m):
        if rep[v] != v:
            continue
        ordinal += 1
        if root_ordinals is not None and ordinal not in root_ordinals:
            continue
        p = 0
        for u in range(v + 1, m):
            if rep[u] >= v and (adjacency[v] >> u) & 1:
                p |= 1 << u
        visit(p, target - 1)
        roots.append(ordinal)
    if root_ordinals is not None:
        assert set(roots) == root_ordinals, 'requested root not present'
    marker = b'ENDPROOF' if root_ordinals is None else b'ENDROOTS'
    assert stream.read(len(marker)) == marker, 'missing completion marker'
    assert stream.read(1) == b'', 'trailing proof data'
    stream.close()
    h = hashlib.sha256()
    with open(proof, 'rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return dict(verified=True, order=n, target=target, nodes=nodes,
                roots=len(roots), scope='full' if root_ordinals is None else sorted(roots),
                seconds=time.monotonic() - started, proof_sha256=h.hexdigest(),
                catalogue_sha256=hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('catalogue')
    ap.add_argument('proof')
    ap.add_argument('target', type=int)
    ap.add_argument('--roots', help='comma separated canonical root ordinals')
    args = ap.parse_args()
    scope = None if args.roots is None else set(map(int, args.roots.split(',')))
    print(json.dumps(audit(args.catalogue, args.proof, args.target, scope), indent=2))
