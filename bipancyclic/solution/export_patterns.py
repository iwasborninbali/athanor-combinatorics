"""Export search-side patterns in a small C++ input format."""
from pathlib import Path
import argparse
from patterns import build_all

ap = argparse.ArgumentParser()
ap.add_argument('--chords', type=int, default=4)
args = ap.parse_args()
data = build_all(args.chords)
lines = [str(len(data))]
for p in data:
    lines.append(f"{p['id']} {p['m']} {len(p['cycles'])} {args.chords}")
    lines.append(' '.join(str(v) for e in p['pairs'] for v in e))
    lines.extend(f"{sum(1 << i for i in c['arcs'])} {c['chords']} {c['chord_mask']}" for c in p['cycles'])
Path(f'patterns{args.chords}.txt').write_text('\n'.join(lines)+'\n')
