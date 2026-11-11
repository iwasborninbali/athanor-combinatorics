#!/usr/bin/env python3
"""Check a streamed clique refutation using stdlib only.

No search module or binary is imported. A byte at each node specifies a
proper colouring to check: a row index, 254 for a deterministic independent
set partition, or 253 for a cardinality leaf. Colour choices are advice;
their validity, all required children, D4 root coverage, and end marker are
checked from the input permutations. Incomplete runs are rejected.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time


def verify_hall_cut(arrays, selected, candidates, rows_mask, target):
    n = len(arrays[0])
    assert target == n-1 and 0 < rows_mask < (1 << n)
    full = (1 << n)-1
    used = [0]*n
    support = [0]*n
    for v in selected:
        for r, c in enumerate(arrays[v]):
            assert not used[r] & (1 << c), 'selected arrays overlap'
            used[r] |= 1 << c
    for v in candidates:
        for r, c in enumerate(arrays[v]):
            assert not used[r] & (1 << c), 'candidate overlaps selection'
            support[r] |= 1 << c
    allowed = []
    forced = []
    for r in range(n):
        vacant = full ^ used[r]
        missing = vacant & ~support[r]
        assert missing.bit_count() <= 1
        allowed.append(missing if missing else vacant)
        if missing:
            forced.append((r, missing.bit_length()-1))
    neighbors = 0
    for r in range(n):
        if rows_mask >> r & 1:
            neighbors |= allowed[r]
    assert neighbors.bit_count() < rows_mask.bit_count(), 'no Hall deficiency'
    return {'forced_holes': forced, 'hall_rows_mask': rows_mask,
            'possible_columns_mask': neighbors,
            'deficit': rows_mask.bit_count()-neighbors.bit_count()}


def verify(catalogue, proof_path, target):
    source = Path(catalogue).read_bytes()
    lines = [tuple(map(int, x.split())) for x in source.decode().splitlines() if x.strip()]
    n, size = lines.pop(0)
    assert 0 < n < 253 and len(lines) == size
    arrays = lines
    lookup = {a: i for i, a in enumerate(arrays)}
    assert len(lookup) == size
    cells = [[0 for _ in range(n)] for _ in range(n)]
    for i, a in enumerate(arrays):
        assert len(a) == n and sorted(a) == list(range(n))
        vectors = {(s-r, a[s]-a[r]) for r in range(n) for s in range(r+1, n)}
        assert len(vectors) == n*(n-1)//2
        for r, c in enumerate(a):
            cells[r][c] |= 1 << i
    # Column partitions are also proper colourings, indexed n..2*n-1.
    cells += [[cells[r][c] for r in range(n)] for c in range(n)]
    all_vertices = (1 << size)-1
    neighbors = []
    representatives = []
    for i, a in enumerate(arrays):
        conflicts = 0
        for r, c in enumerate(a):
            conflicts |= cells[r][c]
        neighbors.append(all_vertices ^ conflicts)
        images = []
        # Independent D4 implementation: optional transpose then optional
        # reversal of the row and column coordinates.
        for transpose in (False, True):
            for reverse_row in (False, True):
                for reverse_col in (False, True):
                    out = [-1]*n
                    for row, col in enumerate(a):
                        x, y = (col, row) if transpose else (row, col)
                        if reverse_row:
                            x = n-1-x
                        if reverse_col:
                            y = n-1-y
                        out[x] = y
                    images.append(lookup[tuple(out)])
        representatives.append(min(images))
    nodes = 0
    start = time.monotonic()
    same_colour_allowed = [all_vertices ^ row ^ (1 << i) for i, row in enumerate(neighbors)]

    def bits(mask):
        while mask:
            b = mask & -mask
            yield b.bit_length()-1
            mask ^= b

    with gzip.open(proof_path, 'rb') as stream:
        selected = []
        def node(candidates, need):
            nonlocal nodes
            nodes += 1
            if nodes % 1048576 == 0:
                print(f'verified_nodes={nodes} seconds={time.monotonic()-start:.1f}', file=sys.stderr, flush=True)
            assert need > 0
            op = stream.read(1)
            assert op, ('truncated node', nodes)
            op = op[0]
            if op == 252:
                encoded = stream.read(4)
                assert len(encoded) == 4
                mask = int.from_bytes(encoded, 'little')
                verify_hall_cut(arrays, selected, list(bits(candidates)), mask, target)
                return
            if op == 253:
                assert candidates.bit_count() < need, ('bad cardinality leaf', nodes)
                return
            if op < 2*n:
                groups = [candidates & group for group in cells[op]]
                groups = [g for g in groups if g]
                groups.sort(key=lambda g: (-g.bit_count(), (g & -g).bit_length()-1))
            else:
                assert op in (251, 254), ('unknown opcode', op)
                # Decode the deterministic independent-set partition.
                groups = []
                remaining = candidates
                while remaining:
                    available, group = remaining, 0
                    while available:
                        bit = available & -available
                        v = bit.bit_length()-1
                        group |= bit
                        remaining ^= bit
                        # Retain only other vertices nonadjacent to every
                        # member already placed in this colour class.
                        available &= same_colour_allowed[v]
                    groups.append(group)
                if op == 251:
                    vertices = list(bits(candidates))
                    assert len(vertices) <= 64
                    count = stream.read(1)
                    assert len(count) == 1
                    encoded = stream.read(2*count[0])
                    assert len(encoded) == 2*count[0]
                    membership = {v: c for c, group in enumerate(groups) for v in bits(group)}
                    for offset in range(0, len(encoded), 2):
                        position, destination = encoded[offset:offset+2]
                        assert position < len(vertices) and destination < len(groups)
                        v = vertices[position]
                        assert not neighbors[v] & groups[destination], 'improper recolouring move'
                        bit = 1 << v
                        old = membership[v]
                        groups[old] ^= bit
                        groups[destination] |= bit
                        membership[v] = destination
                    groups = [g for g in groups if g]
            cover = 0
            for group in groups:
                assert group and not cover & group
                # Row/column groups share one cell. Greedy groups are
                # independent by the successive nonneighbor intersections
                # above. Thus neither construction trusts an untested
                # arbitrary partition supplied by the search.
                cover |= group
            assert cover == candidates
            # Each colour class contributes at most one clique vertex.
            # Branches partition solutions by their greatest vertex in this
            # node's explicit order. Prefixes with <need colours are closed.
            for colour in range(len(groups), 0, -1):
                if colour < need:
                    break
                group = groups[colour-1]
                while group:
                    v = group.bit_length()-1
                    bit = 1 << v
                    group ^= bit
                    assert need > 1, ('refutation contains a target clique', nodes, v)
                    selected.append(v)
                    node(candidates & neighbors[v], need-1)
                    selected.pop()
                    candidates ^= bit

        roots = 0
        for i in range(size):
            if representatives[i] != i:
                continue
            candidates = 0
            for j in bits(neighbors[i]):
                if j > i and representatives[j] >= i:
                    candidates |= 1 << j
            selected[:] = [i]
            node(candidates, target-1)
            roots += 1
        assert stream.read(8) == b'ENDPROOF', 'missing completion marker'
        assert stream.read(1) == b'', 'trailing proof data'
    return {'verified': True, 'order': n, 'excluded_clique_size': target,
            'nodes': nodes, 'roots': roots, 'seconds': time.monotonic()-start,
            'catalogue_sha256': hashlib.sha256(source).hexdigest(),
            'proof_sha256': hashlib.sha256(Path(proof_path).read_bytes()).hexdigest()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('catalogue')
    ap.add_argument('proof')
    ap.add_argument('target', type=int)
    args = ap.parse_args()
    print(json.dumps(verify(args.catalogue, args.proof, args.target), indent=2))
