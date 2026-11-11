#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
while ! test -s logs/full_even.json || ! test -s logs/full_odd.json; do sleep 20; done
# Do not compete with the extra checks on CPU 3.
while kill -0 995441 2>/dev/null; do sleep 10; done
python3 merge_proof.py >logs/merge_order13.json
python3 cleanup_embedded_roots.py >logs/root_cleanup.log
g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_roots.cpp -lz -o checkers/check_roots
python3 scope_regression.py
for residue in 0 1; do
 checkers/check_roots data/costas_11.txt "logs/scope_regression11_${residue}.proof.gz" 11 2 "$residue" >"logs/scope_regression11_${residue}.json" 2>"logs/scope_regression11_${residue}.stderr"
done
# This checker is independent of the search. Only root selection and ENDROOTS
# differ from the copied original checker; together the two scopes cover all roots.
(
 set -o pipefail
 python3 stream_scope.py 0 | AUDIT_ROOT_LOG=logs/check13_even.roots.jsonl /usr/bin/time -v -o logs/check13_even.time checkers/check_roots data/costas_13.txt /dev/stdin 12 2 0 >logs/check13_even.json 2>logs/check13_even.stderr
) &
even_check=$!
taskset -c 3 bash -c 'set -euo pipefail; python3 stream_scope.py 1 | AUDIT_ROOT_LOG=logs/check13_odd.roots.jsonl /usr/bin/time -v -o logs/check13_odd.time checkers/check_roots data/costas_13.txt /dev/stdin 12 2 1 >logs/check13_odd.json 2>logs/check13_odd.stderr' &
odd_check=$!
printf 'even_scope_checker_pid=%s\nodd_scope_checker_pid=%s\n' "$even_check" "$odd_check" >logs/check13.pids
wait "$even_check"
wait "$odd_check"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
p=Path('certificates/order13_manifest.json');d=json.loads(p.read_text())
v=[json.loads(Path(f'logs/check13_{name}.json').read_text()) for name in ['even','odd']]
for residue,x in enumerate(v):
 assert x['verified'] and x['modulus']==2 and x['residue']==residue and x['order']==13 and x['excluded_clique_size']==12
 assert x['roots']==len(range(residue,d['roots'],2))
assert sum(x['nodes'] for x in v)==d['nodes'] and sum(x['roots'] for x in v)==d['roots']
expected={r['ordinal']:r for r in d['root_records']}
for residue,name in enumerate(['even','odd']):
 audited=[json.loads(s) for s in Path(f'logs/check13_{name}.roots.jsonl').read_text().splitlines()]
 assert [r['ordinal'] for r in audited]==list(range(residue,d['roots'],2))
 for r in audited:
  e=expected[r['ordinal']];assert r['vertex']==e['vertex'] and r['nodes']==e['nodes']==e['uncompressed_bytes']
h=hashlib.sha256()
with open(d['proof'],'rb') as f:
 for b in iter(lambda:f.read(1<<20),b''):h.update(b)
assert h.hexdigest()==d['proof_sha256']
d['status']='EXHAUSTED_INDEPENDENTLY_VERIFIED';d['verification']={'method':'copied independent checker with explicit modulo-2 root selection; both disjoint scopes cover every canonical root','scopes':v}
p.write_text(json.dumps(d,indent=2)+'\n')
Path('logs/full_check13.json').write_text(json.dumps(dict(verified=True,order=13,excluded_clique_size=12,nodes=d['nodes'],roots=d['roots'],method=d['verification']['method'],scopes=v),indent=2)+'\n')
PY
