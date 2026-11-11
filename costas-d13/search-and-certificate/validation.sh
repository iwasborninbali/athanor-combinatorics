#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
code=src/fast512
for spec in '9 8' '9 9' '10 10' '12 12'; do
 read -r n k <<< "$spec"
 "$code" "data/costas_${n}.txt" "$k" 120 "certificates/new_${n}_${k}" proof >"logs/valid_${n}_${k}.stdout" 2>"logs/valid_${n}_${k}.stderr"
 if test -f "certificates/new_${n}_${k}.witness.json"; then
  python3 checkers/check.py "certificates/new_${n}_${k}.witness.json" --catalogue "data/costas_${n}.txt" >"logs/valid_${n}_${k}_check.json"
 else
  checkers/check_trace "data/costas_${n}.txt" "certificates/new_${n}_${k}.proof.gz" "$k" >"logs/valid_${n}_${k}_cpp.json" 2>"logs/valid_${n}_${k}_cpp.stderr"
  python3 checkers/check_clique_proof.py "data/costas_${n}.txt" "certificates/new_${n}_${k}.proof.gz" "$k" >"logs/valid_${n}_${k}_python.json" 2>"logs/valid_${n}_${k}_python.stderr"
 fi
done
checkers/check_trace data/costas_11.txt logs/fast512_11.proof.gz 11 >logs/fast512_11_check.json 2>logs/fast512_11_check.stderr
python3 checkers/check_clique_proof.py data/costas_11.txt logs/fast512_11.proof.gz 11 >logs/fast512_11_python.json 2>logs/fast512_11_python.stderr
python3 - <<'PY'
import gzip,hashlib,json
from pathlib import Path
result={}
for name in ['clique_early_11_pilot','fast256_11','fast512_11']:
 p=Path('logs')/(name+'.proof.gz');x=gzip.open(p,'rb').read();result[name]={'trace_bytes':len(x),'trace_sha256':hashlib.sha256(x).hexdigest()}
a=gzip.open('logs/clique_early_13_r0_pilot.proof.gz','rb').read()
for name in ['fast256_13_r0','fast512_13_r0']:
 b=gzip.open('logs/'+name+'.proof.gz','rb').read();result[name]={'equal_baseline':a==b,'trace_bytes':len(b),'trace_sha256':hashlib.sha256(b).hexdigest()}
Path('logs/trace_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
PY
