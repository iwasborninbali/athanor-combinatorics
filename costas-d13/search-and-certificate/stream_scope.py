#!/usr/bin/env python3
"""Stream selected embedded gzip members, hash checked, then ENDROOTS."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

residue = int(sys.argv[1])
assert residue in (0, 1)
m = json.loads(Path('certificates/order13_manifest.json').read_text())
out = sys.stdout.buffer
with open(m['proof'], 'rb') as source:
    offset = 0
    for record in m['root_records']:
        length = record['bytes']
        if record['ordinal'] % 2 == residue:
            source.seek(offset)
            remain = length
            h = hashlib.sha256()
            while remain:
                block = source.read(min(remain, 1 << 20))
                assert block, 'truncated combined certificate'
                h.update(block)
                out.write(block)
                remain -= len(block)
            assert h.hexdigest() == record['sha256'], 'embedded member hash mismatch'
        offset += length
    assert offset + len(gzip.compress(b'ENDPROOF', compresslevel=1, mtime=0)) == m['proof_bytes']
out.write(gzip.compress(b'ENDROOTS', compresslevel=1, mtime=0))
out.flush()
