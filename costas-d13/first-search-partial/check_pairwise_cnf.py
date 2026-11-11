#!/usr/bin/env python3
"""Independently check the direct-conflict exact-cover CNF (stdlib only).

The search/generator executable is never called or imported. This checks a
canonical gzip formula clause-for-clause using independently built per-cell
incidence bitsets. Optional DRAT checking uses the separate drat-trim binary.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time


def verify(catalogue, cnf, full=False):
    raw = Path(catalogue).read_bytes()
    rows = [tuple(map(int, x.split())) for x in raw.decode().splitlines() if x.strip()]
    n, m = rows.pop(0)
    assert len(rows) == len(set(rows)) == m
    cells = [[0]*n for _ in range(n)]
    for i, a in enumerate(rows):
        assert len(a) == n and sorted(a) == list(range(n))
        assert len({(j-r, a[j]-a[r]) for r in range(n) for j in range(r+1, n)}) == n*(n-1)//2
        for r, c in enumerate(a):
            cells[r][c] |= 1 << i
    def indices(mask):
        while mask:
            b = mask & -mask
            yield b.bit_length()-1
            mask ^= b
    count = 0
    with gzip.open(cnf, 'rt') as stream:
        header = stream.readline().split()
        assert header[:2] == ['p', 'cnf']
        declared_variables, declared_clauses = map(int, header[2:])
        def clause(literals):
            nonlocal count
            expected = ' '.join(map(str, literals))+' 0\n'
            assert stream.readline() == expected, ('wrong clause', count+1)
            count += 1
        for i, a in enumerate(rows):
            overlapping = 0
            for r, c in enumerate(a):
                overlapping |= cells[r][c]
            earlier = list(indices(overlapping & ((1 << i)-1)))
            # Batch one independently reconstructed graph row.
            expected = ''.join(f'{-i-1} {-j-1} 0\n' for j in earlier)
            assert stream.read(len(expected)) == expected, ('wrong conflicts', i)
            count += len(earlier)
        for i, a in enumerate(rows):
            for r, c in enumerate(a):
                clause([-i-1, -m-1-r*n-c])
        for r in range(n):
            for c in range(n):
                clause([i+1 for i in indices(cells[r][c])]+[m+1+r*n+c])
        if full:
            for c in range(n*n):
                clause([-m-1-c])
        else:
            for r in range(n):
                clause([m+1+r*n+c for c in range(n)])
            for c in range(n):
                clause([m+1+r*n+c for r in range(n)])
            for r in range(n):
                for c in range(n):
                    for d in range(c):
                        clause([-m-1-r*n-c, -m-1-r*n-d])
            for c in range(n):
                for r in range(n):
                    for s in range(r):
                        clause([-m-1-r*n-c, -m-1-s*n-c])
        p = m+n*n+1
        clause([-p, 1])
        clause([-1, p])
        for i in range(1, m):
            clause([-p-i+1, p+i])
            clause([-i-1, p+i])
            clause([-p-i, p+i-1, i+1])
        lookup = {a: i for i, a in enumerate(rows)}
        for i, a in enumerate(rows):
            orbit = []
            for transpose in (False, True):
                for rx in (False, True):
                    for ry in (False, True):
                        image = [None]*n
                        for r, c in enumerate(a):
                            x, y = (c, r) if transpose else (r, c)
                            if rx: x = n-1-x
                            if ry: y = n-1-y
                            image[x] = y
                        orbit.append(lookup[tuple(image)])
            j = min(orbit)
            if j < i:
                clause([-i-1, p+j])
        assert not stream.read(), 'trailing CNF content'
        assert count == declared_clauses and declared_variables == 2*m+n*n
    return {'encoding_verified': True, 'order': n, 'target': n if full else n-1,
            'variables': declared_variables, 'clauses': count,
            'catalogue_sha256': hashlib.sha256(raw).hexdigest(),
            'cnf_gzip_sha256': hashlib.sha256(Path(cnf).read_bytes()).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('catalogue')
    ap.add_argument('cnf')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--proof')
    ap.add_argument('--seconds', type=int, default=3600)
    ap.add_argument('--proof-log', default='logs/drat_pairwise.log')
    args = ap.parse_args()
    start = time.monotonic()
    result = verify(args.catalogue, args.cnf, args.full)
    if args.proof:
        # Stream the expanded CNF through a workspace-local POSIX FIFO, so
        # even the direct binary encoding stays below the folder disk cap.
        import tempfile
        assert shutil.disk_usage('.').free >= 3*1024**3
        with tempfile.TemporaryDirectory(dir='.', prefix='drat-pairwise-') as tmp:
            expanded = Path(tmp)/'input.cnf'
            os.mkfifo(expanded)
            failures = []
            def feed_cnf():
                try:
                    with gzip.open(args.cnf, 'rb') as src, expanded.open('wb') as dst:
                        shutil.copyfileobj(src, dst)
                except BrokenPipeError:
                    pass
                except Exception as exc:
                    failures.append(str(exc))
            with Path(args.proof_log).open('wb') as log:
                proc = subprocess.Popen(['drat-trim', str(expanded), '-i', '-t', str(args.seconds)], stdin=subprocess.PIPE, stdout=log, stderr=log)
                writer = threading.Thread(target=feed_cnf)
                writer.start()
                try:
                    with gzip.open(args.proof, 'rb') as src:
                        shutil.copyfileobj(src, proc.stdin)
                    proc.stdin.close()
                except BrokenPipeError:
                    pass
                code = proc.wait()
                writer.join()
            assert not failures, failures
            text = Path(args.proof_log).read_text(errors='replace')
            assert code == 0 and 's VERIFIED' in text
        result['unsat_proof_verified'] = True
        result['proof_sha256'] = hashlib.sha256(Path(args.proof).read_bytes()).hexdigest()
    result['seconds'] = time.monotonic()-start
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
