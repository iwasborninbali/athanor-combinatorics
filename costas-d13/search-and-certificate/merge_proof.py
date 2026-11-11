#!/usr/bin/env python3
"""Join complete per-root gzip members; never trusts a root count alone."""
import argparse
import gzip
import hashlib
import json
import os
import shutil
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def canonical_vertices(path):
    rows = [tuple(map(int, line.split())) for line in Path(path).read_text().splitlines() if line.strip()]
    n, count = rows.pop(0)
    assert len(rows) == count
    lookup = {a: v for v, a in enumerate(rows)}
    roots = []
    for v, a in enumerate(rows):
        orbit = []
        p = a
        for _ in range(4):
            orbit.append(lookup[tuple(p)])
            orbit.append(lookup[tuple(n - 1 - c for c in p)])
            q = [0] * n
            for r, c in enumerate(p):
                q[c] = n - 1 - r
            p = q
        if v == min(orbit):
            roots.append(v)
    return roots


def merge(folder):
    folder = Path(folder)
    roots = canonical_vertices(folder / 'data/costas_13.txt')
    records = {}
    summaries = {}
    for residue, name in enumerate(['full_even', 'full_odd']):
        summary = json.loads((folder / f'logs/{name}.json').read_text())
        assert summary['status'] == 'EXHAUSTED' and summary['cut_roots'] == 0
        assert summary['order'] == 13 and summary['target'] == 12
        summaries[name] = summary
        part = [json.loads(line) for line in (folder / f'logs/{name}.roots.jsonl').read_text().splitlines()]
        expected = set(range(residue, len(roots), 2))
        assert {r['ordinal'] for r in part} == expected
        assert len(part) == len(expected) == summary['roots']
        assert sum(r['nodes'] for r in part) == summary['nodes']
        for r in part:
            ordinal = r['ordinal']
            assert r['complete'] is True and r['vertex'] == roots[ordinal]
            assert ordinal not in records
            path = folder / f'logs/{name}.r{ordinal}.proof.gz'
            assert path.is_file() and path.stat().st_size > 0
            # Production traces use one byte per node; validate that contract
            # independently, including gzip CRC/footer and root boundaries.
            decoded_bytes = 0
            allowed = bytes(range(26)) + bytes([253, 254])
            with gzip.open(path, 'rb') as decoded:
                for block in iter(lambda: decoded.read(1 << 20), b''):
                    decoded_bytes += len(block)
                    assert not block.translate(None, allowed), 'non-production opcode'
            assert decoded_bytes == r['nodes'], 'root trace length disagrees with node count'
            records[ordinal] = {**r, 'path': str(path.relative_to(folder)), 'bytes': path.stat().st_size, 'uncompressed_bytes': decoded_bytes, 'sha256': sha(path)}
    assert set(records) == set(range(len(roots)))
    # A global verifier, not this merger, validates the uncompressed trees and gzip integrity.
    out = folder / 'certificates/no_12_order13.proof.gz'
    tmp = out.with_suffix(out.suffix + '.tmp')
    # Preserve an explicit recovery map before moving bytes into the archive.
    # Exact original gzip members can be recovered by the recorded byte lengths.
    plan = folder / 'certificates/order13_merge_plan.json'
    with plan.open('w') as record:
        json.dump(dict(output=str(out.relative_to(folder)), temporary=str(tmp.relative_to(folder)),
                       root_records=[records[o] for o in range(len(roots))]), record, indent=2)
        record.write('\n');record.flush();os.fsync(record.fileno())
    with tmp.open('wb') as dest:
        for ordinal in range(len(roots)):
            original = folder / records[ordinal]['path']
            with original.open('rb') as source:
                shutil.copyfileobj(source, dest)
            dest.flush();os.fsync(dest.fileno())
            original.unlink()  # duplicate bytes now durably embedded, with recovery map
        dest.write(gzip.compress(b'ENDPROOF', compresslevel=1, mtime=0))
        dest.flush();os.fsync(dest.fileno())
    tmp.replace(out)
    manifest = dict(order=13, excluded_target=12, status='SEARCH_EXHAUSTED_AWAITING_INDEPENDENT_CHECK',
                    catalogue_sha256=sha(folder / 'data/costas_13.txt'),
                    roots=len(roots), nodes=sum(r['nodes'] for r in records.values()),
                    search_core_seconds=sum(s['seconds'] for s in summaries.values()),
                    root_core_seconds=sum(r['seconds'] for r in records.values()),
                    proof=str(out.relative_to(folder)), proof_bytes=out.stat().st_size,
                    proof_sha256=sha(out), root_records=[records[o] for o in range(len(roots))],
                    original_root_members='embedded verbatim; recoverable by byte lengths in canonical order',
                    summaries=summaries)
    (folder / 'certificates/order13_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('folder', nargs='?', default='.')
    args = ap.parse_args()
    result = merge(args.folder)
    print(json.dumps({k: v for k, v in result.items() if k not in ('root_records', 'summaries')}, indent=2))
