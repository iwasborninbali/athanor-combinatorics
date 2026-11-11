"""SAT exact cover with a complementary permutation; one array variable each.

No solver library is required to generate the formula. This is discovery-side
code; check_sat_encoding.py reconstructs and checks it independently.
"""
import argparse
from pathlib import Path
import hashlib
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('order', type=int)
    ap.add_argument('--symmetry', action='store_true')
    ap.add_argument('--full', action='store_true', help='full packing, for certified pilot cases')
    ap.add_argument('--amo', choices=['sequential', 'binary'], default='sequential')
    args = ap.parse_args()
    path = Path(f'data/costas_{args.order}.txt')
    words = list(map(int, path.read_text().split()))
    n, m = words[:2]
    arrays = [tuple(words[2+i*n:2+(i+1)*n]) for i in range(m)]
    assert n == args.order and len(words) == 2+n*m
    variables = m+n*n
    clauses = []
    def new():
        nonlocal variables
        variables += 1
        return variables
    def exactly_one(lits):
        clauses.append(lits[:])
        # Sinz sequential AMO. Each s_j means some earlier literal is true.
        if len(lits) <= 1:
            return
        if args.amo == 'binary':
            bits = [new() for _ in range((len(lits)-1).bit_length())]
            for code, literal in enumerate(lits):
                for bit, variable in enumerate(bits):
                    clauses.append([-literal, variable if code >> bit & 1 else -variable])
            return
        chain = [new() for _ in range(len(lits)-1)]
        clauses.append([-lits[0], chain[0]])
        for i in range(1, len(lits)-1):
            clauses.append([-lits[i], chain[i]])
            clauses.append([-chain[i-1], chain[i]])
            clauses.append([-lits[i], -chain[i-1]])
        clauses.append([-lits[-1], -chain[-1]])
    groups = [[] for _ in range(n*n)]
    for i, a in enumerate(arrays):
        for r, c in enumerate(a):
            groups[r*n+c].append(i+1)
    holes = [m+i+1 for i in range(n*n)]
    for i, group in enumerate(groups):
        exactly_one(group+[holes[i]])
    if args.full:
        clauses.extend([[-h] for h in holes])
    else:
        for r in range(n):
            exactly_one(holes[r*n:(r+1)*n])
        for c in range(n):
            exactly_one([holes[r*n+c] for r in range(n)])
    if args.symmetry:
        lookup = {a: i for i, a in enumerate(arrays)}
        prefix = [new() for _ in range(m)]
        # prefix[i] iff at least one of x[0],...,x[i] is selected.
        clauses += [[-prefix[0], 1], [-1, prefix[0]]]
        for i in range(1, m):
            clauses += [[-prefix[i-1], prefix[i]], [-i-1, prefix[i]],
                        [-prefix[i], prefix[i-1], i+1]]
        for i, a in enumerate(arrays):
            orbit = []
            for transpose in (0, 1):
                for rx in (0, 1):
                    for ry in (0, 1):
                        b = [-1]*n
                        for r, c in enumerate(a):
                            x, y = (c, r) if transpose else (r, c)
                            if rx: x = n-1-x
                            if ry: y = n-1-y
                            b[x] = y
                        orbit.append(lookup[tuple(b)])
            j = min(orbit)
            if j < i:
                clauses.append([-i-1, prefix[j]])
    stem = ('full' if args.full else 'holes')+f'_{n}' + ('_sym' if args.symmetry else '')
    if args.amo != 'sequential':
        stem += '_'+args.amo
    cnf = Path(f'data/{stem}.cnf')
    with cnf.open('w') as f:
        f.write(f'p cnf {variables} {len(clauses)}\n')
        for clause in clauses:
            f.write(' '.join(map(str, clause))+' 0\n')
    record = {'order': n, 'target': n if args.full else n-1, 'arrays': m, 'full': args.full, 'amo': args.amo,
              'array_variables': [1, m], 'hole_variables': [m+1, m+n*n],
              'variables': variables, 'clauses': len(clauses), 'symmetry': args.symmetry,
              'catalogue_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'cnf_sha256': hashlib.sha256(cnf.read_bytes()).hexdigest()}
    Path(f'data/{stem}.meta.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
