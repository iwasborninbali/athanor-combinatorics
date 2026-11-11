#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING baseline/timed_baseline.cpp -lz -o baseline/clique_early
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING src/clique_speed.cpp -lz -o src/clique_speed
g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp -lz -o checkers/check_trace
for code in baseline/clique_early src/clique_speed; do
 label=$(basename "$code")
 "$code" data/costas_11.txt 11 300 "logs/${label}_11_pilot" proof >"logs/${label}_11_pilot.stdout" 2>"logs/${label}_11_pilot.stderr"
 checkers/check_trace data/costas_11.txt "logs/${label}_11_pilot.proof.gz" 11 >"logs/${label}_11_check.json" 2>"logs/${label}_11_check.stderr"
 "$code" data/costas_13.txt 12 600 "logs/${label}_13_r0_pilot" proof 0 0 1 >"logs/${label}_13_r0_pilot.stdout" 2>"logs/${label}_13_r0_pilot.stderr"
done
python3 - <<'PY'
import gzip
from pathlib import Path
p=Path('logs')
a=gzip.open(p/'clique_early_11_pilot.proof.gz','rb').read()
b=gzip.open(p/'clique_speed_11_pilot.proof.gz','rb').read()
print('order11 trace equal:', a==b, len(a),len(b))
a=gzip.open(p/'clique_early_13_r0_pilot.proof.gz','rb').read()
b=gzip.open(p/'clique_speed_13_r0_pilot.proof.gz','rb').read()
print('order13 root0 trace equal:', a==b,len(a),len(b))
PY
