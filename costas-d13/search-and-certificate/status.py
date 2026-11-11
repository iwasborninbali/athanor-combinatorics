#!/usr/bin/env python3
"""Read-only, lightweight VM progress line (no search and no provider calls)."""
import datetime
import json
import re
from pathlib import Path

parts = []
phase = 'search'
for name in ['full_even', 'full_odd']:
    summary = Path(f'logs/{name}.json')
    trace = Path(f'logs/{name}.stderr')
    if summary.exists() and summary.stat().st_size:
        d = json.loads(summary.read_text())
        parts.append(f"{name.removeprefix('full_')}: {d['nodes']:,} states, {d['roots']} roots, {d['status']}")
    elif trace.exists():
        lines = trace.read_text().splitlines()
        last = next((line for line in reversed(lines) if re.search(r'\bnodes=\d+', line)), '')
        found = re.search(r'\bnodes=(\d+)', last)
        roots = Path(f'logs/{name}.roots.jsonl')
        count = len(roots.read_text().splitlines()) if roots.exists() else 0
        parts.append(f"{name.removeprefix('full_')}: {int(found.group(1)):,} states, {count} complete roots" if found else f'{name}: starting')
for name in ['even', 'odd']:
    f = Path(f'logs/check13_{name}.stderr')
    result = Path(f'logs/check13_{name}.json')
    if result.exists() and result.stat().st_size:
        d = json.loads(result.read_text())
        parts.append(f"audit {name}: verified {d['nodes']:,} states")
        phase = 'verified_scope'
    elif f.exists():
        phase = 'verification'
        lines = f.read_text().splitlines()
        parts.append(f'audit {name}: {lines[-1] if lines else "starting"}')
manifest = Path('certificates/order13_manifest.json')
if manifest.exists():
    status = json.loads(manifest.read_text())['status']
    if status == 'EXHAUSTED_INDEPENDENTLY_VERIFIED':
        phase = 'complete'
        parts.append('full exclusion independently verified')
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'), phase=phase, text='; '.join(parts))))
