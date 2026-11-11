#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
# Waiting is light; both search cores remain reserved for their own jobs.
while ! test -f logs/full_even.json || ! test -f logs/full_odd.json; do sleep 20; done
python3 merge_proof.py >logs/merge_order13.json
# Existing checker, unchanged. One full stream, all canonical roots and EOF.
/usr/bin/time -v -o logs/full_check13.time checkers/check_trace data/costas_13.txt certificates/no_12_order13.proof.gz 12 >logs/full_check13.json 2>logs/full_check13.stderr
python3 - <<'PY'
import json
from pathlib import Path
p=Path('certificates/order13_manifest.json');d=json.loads(p.read_text());v=json.loads(Path('logs/full_check13.json').read_text())
assert v['verified'] and v['nodes']==d['nodes'] and v['roots']==d['roots'] and v['excluded_clique_size']==12
d['status']='EXHAUSTED_INDEPENDENTLY_VERIFIED';d['verification']=v;p.write_text(json.dumps(d,indent=2)+'\n')
PY
