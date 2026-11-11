#!/usr/bin/env python3
"""Stdlib driver for the additional C++ verifier; pure-Python alternative:
check_clique_proof.py. This driver explicitly requires ./check_trace.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('catalogue')
ap.add_argument('proof')
ap.add_argument('target', type=int)
args = ap.parse_args()
result = subprocess.run(['./check_trace', args.catalogue, args.proof, str(args.target)], stdout=subprocess.PIPE, text=True, check=True)
record = json.loads(result.stdout)
assert record['verified'] and record['excluded_clique_size'] == args.target
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
record.update(catalogue_sha256=sha(args.catalogue), proof_sha256=sha(args.proof),
              verifier_source_sha256=sha('check_trace.cpp'),
              verifier_binary_sha256=sha('check_trace'))
print(json.dumps(record, indent=2))
