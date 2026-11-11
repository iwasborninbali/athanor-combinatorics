#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING baseline/timed_baseline.cpp -lz -o baseline/clique_early_bench
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=512 src/clique_fast.cpp -lz -o src/clique_fast
sha256sum baseline/clique_early_bench src/clique_fast src/clique_fast.cpp src/local_fast.hpp >logs/production-SHA256SUMS
for i in 1 2 3; do
 for label in old new; do
  if test "$label" = old; then code=baseline/clique_early_bench; else code=src/clique_fast; fi
  /usr/bin/time -v -o "logs/repeat_${label}_11_${i}.time" "$code" data/costas_11.txt 11 120 "logs/repeat_${label}_11_${i}" proof >"logs/repeat_${label}_11_${i}.stdout" 2>"logs/repeat_${label}_11_${i}.stderr"
 done
done
# Fixed before looking at per-root costs: heavy early, middle and late roots.
SPEED_ROOT_LIST=0,20,40,80,160,320,640,1280 /usr/bin/time -v -o logs/sample_old13.time baseline/clique_early_bench data/costas_13.txt 12 5000 logs/sample_old13 proof 0 0 1000000 >logs/sample_old13.stdout 2>logs/sample_old13.stderr
# All even canonical roots, with an independently named trace for each root.
/usr/bin/time -v -o logs/full_even.time src/clique_fast data/costas_13.txt 12 13000 logs/full_even proof 0 0 1000000 2 0 1 >logs/full_even.stdout 2>logs/full_even.stderr
