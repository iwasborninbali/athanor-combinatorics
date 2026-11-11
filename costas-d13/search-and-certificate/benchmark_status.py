#!/usr/bin/env python3
"""Lightweight read-only progress for the final fixed-root comparison."""
import datetime
import json
import re
from pathlib import Path

status=Path('logs/isolated_status.json')
if status.exists():
    print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),done=True,text=status.read_text().strip())))
else:
    parts=[]
    for label in ['old','new']:
        summary=Path(f'logs/iso_{label}_13.json')
        if summary.exists() and summary.stat().st_size:
            d=json.loads(summary.read_text());parts.append(f'{label}: {d["nodes"]:,} states, {d["roots"]} roots, {d["seconds"]:.3f}s, {d["status"]}')
            continue
        log=Path(f'logs/iso_{label}_13.stderr')
        if log.exists():
            found=re.findall(r'nodes=(\d+).*seconds=([\d.]+)',log.read_text())
            parts.append(f'{label}: {int(found[-1][0]):,} states / {found[-1][1]}s so far' if found else f'{label}: starting')
        else:
            parts.append(f'{label}: waiting')
    print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),done=False,text='; '.join(parts))))
