#!/usr/bin/env python3
"""Remove duplicate files only after checking their exact embedded copies."""
import gzip
import hashlib
import json
from pathlib import Path
m = json.loads(Path('certificates/order13_manifest.json').read_text())
with open(m['proof'], 'rb') as f:
    for r in m['root_records']:
        block = f.read(r['bytes'])
        assert len(block) == r['bytes'] and hashlib.sha256(block).hexdigest() == r['sha256']
        path = Path(r['path'])
        if path.exists():
            assert path.stat().st_size == r['bytes']
            path.unlink()
    assert gzip.decompress(f.read()) == b'ENDPROOF', 'invalid combined completion member'
print('Removed duplicate root files; their exact gzip members remain embedded in the full certificate.')
