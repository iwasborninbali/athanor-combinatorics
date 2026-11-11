#!/usr/bin/env python3
"""Build modulo-root regression traces from an already fully checked pilot."""
import gzip
import json
from pathlib import Path
payload = gzip.decompress(Path('logs/fast512_11.proof.gz').read_bytes())
assert payload.endswith(b'ENDPROOF')
records = [json.loads(s) for s in Path('logs/fast512_11.roots.jsonl').read_text().splitlines()]
assert [r['ordinal'] for r in records] == list(range(555))
parts = [bytearray(), bytearray()]
offset = 0
for r in records:
    parts[r['ordinal'] % 2].extend(payload[offset:offset + r['nodes']])
    offset += r['nodes']
assert offset == len(payload) - 8
for residue, part in enumerate(parts):
    Path(f'logs/scope_regression11_{residue}.proof.gz').write_bytes(gzip.compress(bytes(part) + b'ENDROOTS', mtime=0))
