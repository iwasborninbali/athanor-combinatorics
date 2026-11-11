#!/usr/bin/env python3
"""Independent stdlib audit of exact-cover CNF and optional external DRAT check.

Does not import the generator or any search code. An optional proof is checked
by the separately installed drat-trim, streamed from gzip; no expanded proof
is written to disk. Encoding-only success is not an UNSAT certificate.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time


def verify_encoding(catalogue, cnf, symmetry, full=False, amo='sequential'):
    raw = Path(catalogue).read_bytes()
    entries = [tuple(map(int, s.split())) for s in raw.decode().splitlines() if s.strip()]
    n, count = entries.pop(0)
    assert len(entries) == count == len(set(entries))
    for permutation in entries:
        assert len(permutation) == n and sorted(permutation) == list(range(n))
        displacement = [(j-i, permutation[j]-permutation[i])
                        for i in range(n) for j in range(i+1, n)]
        assert len(set(displacement)) == n*(n-1)//2
    variable_count = count + n*n
    checked = 0
    with Path(cnf).open() as stream:
        header = stream.readline().split()
        assert header[:2] == ['p', 'cnf'] and len(header) == 4
        declared_variables, declared_clauses = map(int, header[2:])

        def clause(expected):
            nonlocal checked
            line = stream.readline()
            assert line, ('missing clause', checked+1)
            actual = list(map(int, line.split()))
            assert actual == list(expected)+[0], ('wrong clause', checked+1)
            checked += 1

        def exactly_one(choices):
            nonlocal variable_count
            # Verify a complete cover clause and the standard prefix-chain
            # AMO encoding, with fresh auxiliary variables for this group.
            clause(choices)
            if len(choices) == 1:
                return
            if amo == 'binary':
                width = (len(choices)-1).bit_length()
                bit_variables = range(variable_count+1, variable_count+width+1)
                variable_count += width
                for code, literal in enumerate(choices):
                    for bit, variable in enumerate(bit_variables):
                        clause([-literal, variable if code & (1 << bit) else -variable])
                return
            auxiliary = list(range(variable_count+1, variable_count+len(choices)))
            variable_count += len(auxiliary)
            clause([-choices[0], auxiliary[0]])
            for left, current, previous in zip(choices[1:-1], auxiliary[1:], auxiliary):
                clause([-left, current])
                clause([-previous, current])
                clause([-left, -previous])
            clause([-choices[-1], -auxiliary[-1]])

        # Independently reconstruct incidence directly by each board cell.
        for row in range(n):
            for col in range(n):
                support = [i+1 for i, p in enumerate(entries) if p[row] == col]
                exactly_one(support+[count+1+row*n+col])
        if full:
            for cell in range(n*n):
                clause([-count-1-cell])
        else:
            for row in range(n):
                exactly_one([count+1+row*n+col for col in range(n)])
            for col in range(n):
                exactly_one([count+1+row*n+col for row in range(n)])
        if symmetry:
            prefixes = list(range(variable_count+1, variable_count+count+1))
            variable_count += count
            clause([-prefixes[0], 1])
            clause([-1, prefixes[0]])
            for i in range(1, count):
                clause([-prefixes[i-1], prefixes[i]])
                clause([-i-1, prefixes[i]])
                clause([-prefixes[i], prefixes[i-1], i+1])
            lookup = {a: i for i, a in enumerate(entries)}
            for i, p in enumerate(entries):
                images = []
                rotation = p
                for _ in range(4):
                    images.append(rotation)
                    images.append(tuple(n-1-x for x in rotation))
                    rotated = [None]*n
                    for row, col in enumerate(rotation):
                        rotated[col] = n-1-row
                    rotation = tuple(rotated)
                minimum = min(lookup[q] for q in images)
                if minimum < i:
                    clause([-i-1, prefixes[minimum]])
        assert not stream.read().strip(), 'unexpected extra clauses'
        assert checked == declared_clauses and variable_count == declared_variables
    return {'encoding_verified': True, 'order': n, 'target': n if full else n-1, 'full': full, 'amo': amo,
            'variables': variable_count, 'clauses': checked, 'symmetry': symmetry,
            'catalogue_sha256': hashlib.sha256(raw).hexdigest(),
            'cnf_sha256': hashlib.sha256(Path(cnf).read_bytes()).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('catalogue')
    ap.add_argument('cnf')
    ap.add_argument('--symmetry', action='store_true')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--amo', choices=['sequential', 'binary'], default='sequential')
    ap.add_argument('--proof')
    ap.add_argument('--drat-trim', default='drat-trim')
    ap.add_argument('--proof-log', default='logs/drat_check.log')
    ap.add_argument('--seconds', type=int, default=3600)
    args = ap.parse_args()
    started = time.monotonic()
    result = verify_encoding(args.catalogue, args.cnf, args.symmetry, args.full, args.amo)
    if args.proof:
        command = [args.drat_trim, args.cnf, '-i', '-t', str(args.seconds)]
        with Path(args.proof_log).open('wb') as log:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=log)
            try:
                with gzip.open(args.proof, 'rb') as trace:
                    shutil.copyfileobj(trace, process.stdin, length=1024*1024)
                process.stdin.close()
            except BrokenPipeError:
                pass
            code = process.wait()
        output = Path(args.proof_log).read_text(errors='replace')
        assert code == 0 and 's VERIFIED' in output, (code, output[-1000:])
        result.update(unsat_proof_verified=True,
                      proof_sha256=hashlib.sha256(Path(args.proof).read_bytes()).hexdigest(),
                      proof_checker=command)
    result['seconds'] = time.monotonic()-started
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
