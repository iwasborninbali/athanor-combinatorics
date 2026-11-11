#!/usr/bin/env python3
"""Exact stdlib replay adapted from the independent a05 verifier.

No search code, saved incidence matrix, or saved invariant classes are imported.
The automorphism search recomputes its necessary invariants from the witness.
Run without Python's -O option (the checks deliberately use assertions).
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTIFICATE_SHA256 = 'af7612a2a0a05e64265a7d44ca35039d033e72e40102a1bec2d122ace887727b'


def span(rows):
    values = {0}
    for row in rows:
        values |= {x ^ row for x in values}
    return frozenset(values)


def perp(space):
    return frozenset(x for x in range(64)
                     if all((x & y).bit_count() % 2 == 0 for y in space))


def histogram(values):
    return dict(sorted(Counter(values).items()))


def load_blocks(filename, size):
    raw = (HERE / 'certificates' / filename).read_bytes()
    data = json.loads(raw)
    assert (data['n'], data['k'], data['r']) == (6, 3, 2)
    rows = data['basis_rows']
    assert len(rows) == size
    assert all(len(b) == 3 and all(type(x) is int and 0 < x < 64 for x in b)
               for b in rows)
    blocks = [span(b) for b in rows]
    assert all(len(b) == 8 for b in blocks), 'dependent basis'
    assert len(set(blocks)) == size, 'duplicate subspace'
    return raw, rows, blocks


def line_multiplicities(blocks, lines):
    multiplicities = {line: sum(set(line) <= b for b in blocks) for line in lines}
    assert min(multiplicities.values()) >= 1, 'uncovered two-space'
    assert sum(multiplicities.values()) == 7 * len(blocks)
    return multiplicities


def stable_colors(blocks, multiplicities):
    """Stabilizers preserve these colors, including every refinement round."""
    edge = {(x, y): multiplicities[tuple(sorted((x, y, x ^ y)))]
            for x in range(1, 64) for y in range(1, 64) if x != y}
    colors = {p: sum(p in b for b in blocks) for p in range(1, 64)}
    for _ in range(64):
        signatures = {x: (colors[x], tuple(sorted(Counter(
            (edge[x, y], colors[y]) for y in range(1, 64) if y != x).items())))
            for x in range(1, 64)}
        labels = {s: i for i, s in enumerate(sorted(set(signatures.values())))}
        new = {x: labels[signatures[x]] for x in colors}
        same = all((colors[x] == colors[y]) == (new[x] == new[y])
                   for x in colors for y in colors)
        colors = new
        if same:
            return colors
    raise AssertionError('color refinement did not stabilize')


def compose(a, b):
    return tuple(a[b[x]] for x in range(64))


def map_from_basis_images(images):
    return tuple(xor_images(x, images) for x in range(64))


def xor_images(x, images):
    value = 0
    for i, image in enumerate(images):
        if x & (1 << i):
            value ^= image
    return value


def stabilizer(blocks, multiplicities):
    blocks = frozenset(b - {0} for b in blocks)
    colors = stable_colors(blocks, multiplicities)
    classes = {c: [p for p in range(1, 64) if colors[p] == c]
               for c in set(colors.values())}
    assert sorted(map(len, classes.values())) == [1, 1, 1, 2, 2, 8, 16, 16, 16]
    domain_basis = [17, 14, 38, 5, 1, 2]
    assert len(span(domain_basis)) == 64
    maps = []
    nodes = Counter()

    def extend(depth, mapping):
        nodes[depth] += 1
        if depth == 6:
            if {frozenset(mapping[p] for p in b) for b in blocks} == blocks:
                maps.append(tuple(mapping[p] for p in range(64)))
            return
        v = domain_basis[depth]
        for image in classes[colors[v]]:
            # Current map is an isomorphism on its domain span. Choosing an
            # image outside its image span extends it to an injective map.
            if image in mapping.values():
                continue
            new = {x ^ v: y ^ image for x, y in mapping.items()}
            if any(colors[x] != colors[y] for x, y in new.items()):
                continue
            extend(depth + 1, {**mapping, **new})

    extend(0, {0: 0})
    assert nodes == {0: 1, 1: 1, 2: 1, 3: 2, 4: 16, 5: 256, 6: 4096}
    identity = tuple(range(64))
    generator_images = [[15, 29, 10, 25, 30, 49], [39, 36, 51, 25, 54, 49]]
    g, h = [map_from_basis_images(a) for a in generator_images]
    assert all(len(set(a)) == 64 for a in [g, h])
    assert compose(g, g) == compose(h, h) == identity
    assert compose(g, h) == compose(h, g)
    generated = {identity, g, h, compose(g, h)}
    assert len(generated) == 4 and generated == set(maps)
    point_orbits = {frozenset(a[p] for a in maps) for p in range(1, 64)}
    block_orbits = {frozenset(frozenset(a[p] for p in b) for a in maps)
                    for b in blocks}
    point_hist = histogram(map(len, point_orbits))
    block_hist = histogram(map(len, block_orbits))
    assert point_hist == {1: 7, 2: 12, 4: 8}
    assert block_hist == {1: 8, 2: 24, 4: 12}
    exceptional = frozenset(p for p in range(1, 64)
                            if sum(p in b for b in blocks) > 11)
    assert exceptional == span([14, 17, 38]) - {0}
    assert exceptional not in blocks
    assert all(a[p] == p for a in maps for p in exceptional)
    intersections = histogram(len(b & exceptional) for b in blocks)
    assert intersections == {0: 48, 1: 28, 3: 28}
    return {
        'order': len(maps), 'isomorphism_type': 'C2 x C2',
        'search_nodes_by_depth': dict(sorted(nodes.items())),
        'generator_images_of_standard_basis': generator_images,
        'point_orbit_size_histogram': point_hist,
        'block_orbit_size_histogram': block_hist,
        'exceptional_plane_points': sorted(exceptional),
        'exceptional_plane_fixed_pointwise': True,
        'block_intersections_with_exceptional_plane': intersections,
    }


def check_hashes():
    entries = []
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = HERE / name
        assert path.is_file(), f'missing packaged file: {name}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        entries.append(name)
    assert len(entries) == len(set(entries))
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hashes', action='store_true', help='also check SHA256SUMS')
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are part of this checker')
    hashes = check_hashes() if args.hashes else None
    raw, rows, blocks = load_blocks('cover104.json', 104)
    assert hashlib.sha256(raw).hexdigest() == CERTIFICATE_SHA256
    text_rows = [[int(x) for x in line.split()]
                 for line in (HERE / 'certificates/cover104.txt').read_text().splitlines()
                 if line.strip() and not line.startswith('#')]
    assert text_rows == rows
    lines = sorted({tuple(sorted((x, y, x ^ y)))
                    for x in range(1, 64) for y in range(x + 1, 64)})
    assert len(lines) == 651
    multiplicities = line_multiplicities(blocks, lines)
    hist = histogram(multiplicities.values())
    assert hist == {1: 616, 2: 3, 3: 28, 4: 2, 6: 1, 8: 1}
    private = histogram(sum(multiplicities[line] == 1 for line in lines
                            if set(line) <= b) for b in blocks)
    assert private == {4: 28, 5: 8, 6: 12, 7: 56}
    degrees = histogram(sum(p in b for b in blocks) for p in range(1, 64))
    assert degrees == {11: 56, 12: 2, 16: 3, 20: 2}
    dual_blocks = [perp(b) for b in blocks]
    assert all(len(b) == 8 for b in dual_blocks) and len(set(dual_blocks)) == 104
    four_spaces = [perp(frozenset((0, *line))) for line in lines]
    assert len(set(four_spaces)) == 651 and all(len(s) == 16 for s in four_spaces)
    assert all(any(b <= s for b in dual_blocks) for s in four_spaces)
    original_turan = histogram(sum(b <= s for b in blocks) for s in four_spaces)
    assert original_turan == {0: 36, 1: 524, 2: 76, 3: 8, 4: 7}
    _, _, old_blocks = load_blocks('pavese_105.json', 105)
    old_hist = histogram(line_multiplicities(old_blocks, lines).values())
    assert old_hist == {1: 616, 3: 28, 5: 7}
    old, new = set(old_blocks), set(blocks)
    trade = json.loads((HERE / 'certificates/trade_105_to_104.json').read_text())
    removed = [span(b) for b in trade['removed_basis_rows']]
    added = [span(b) for b in trade['added_basis_rows']]
    assert len(removed) == len(set(removed)) == 95
    assert len(added) == len(set(added)) == 94
    assert old - new == set(removed) and new - old == set(added)
    assert len(old & new) == trade['common_blocks'] == 10
    group = stabilizer(blocks, multiplicities)
    print(json.dumps({
        'status': 'PASS', 'certificate_sha256': CERTIFICATE_SHA256,
        'hashes_checked': hashes, 'blocks': len(blocks), 'two_spaces': len(lines),
        'coverage_multiplicity_histogram': hist, 'incidences': sum(multiplicities.values()),
        'private_two_spaces_per_block_histogram': private,
        'point_degree_histogram': degrees,
        'four_spaces_containing_dual_blocks': len(four_spaces),
        'original_blocks_in_four_spaces_histogram': original_turan,
        'no_correlation_stabilizer': original_turan.get(0, 0) > 0,
        'pavese_105_multiplicity_histogram': old_hist,
        'trade': {'common': 10, 'removed': len(removed), 'added': len(added)},
        'automorphisms': group,
    }, indent=2))


if __name__ == '__main__':
    main()
