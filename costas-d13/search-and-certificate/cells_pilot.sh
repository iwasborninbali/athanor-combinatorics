#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING src/clique_cells64.cpp -lz -o src/cells64
for threshold in 64 128 256 512; do
 g++ -O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=$threshold src/clique_cells.cpp -lz -o "src/cells${threshold}g"
done
for code in cells64 cells64g cells128g cells256g cells512g; do
 "src/$code" data/costas_11.txt 11 300 "logs/${code}_11" proof >"logs/${code}_11.stdout" 2>"logs/${code}_11.stderr"
done
for code in cells64 cells128g cells256g; do
 "src/$code" data/costas_13.txt 12 400 "logs/${code}_13_r0" proof 0 0 1 >"logs/${code}_13_r0.stdout" 2>"logs/${code}_13_r0.stderr"
done
