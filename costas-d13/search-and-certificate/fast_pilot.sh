#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
threshold=$1
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=$threshold src/clique_fast.cpp -lz -o "src/fast${threshold}"
"src/fast${threshold}" data/costas_11.txt 11 300 "logs/fast${threshold}_11" proof >"logs/fast${threshold}_11.stdout" 2>"logs/fast${threshold}_11.stderr"
"src/fast${threshold}" data/costas_13.txt 12 600 "logs/fast${threshold}_13_r0" proof 0 0 1 >"logs/fast${threshold}_13_r0.stdout" 2>"logs/fast${threshold}_13_r0.stderr"
