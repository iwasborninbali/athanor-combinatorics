#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
for threshold in 128 256; do
 g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=$threshold src/clique_mask.cpp -lz -o "src/mask${threshold}"
 "src/mask${threshold}" data/costas_11.txt 11 300 "logs/mask${threshold}_11" proof >"logs/mask${threshold}_11.stdout" 2>"logs/mask${threshold}_11.stderr"
 "src/mask${threshold}" data/costas_13.txt 12 600 "logs/mask${threshold}_13_r0" proof 0 0 1 >"logs/mask${threshold}_13_r0.stdout" 2>"logs/mask${threshold}_13_r0.stderr"
done
