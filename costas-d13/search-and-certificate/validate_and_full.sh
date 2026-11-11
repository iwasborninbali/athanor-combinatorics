#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
bash validation.sh >logs/validation.log 2>&1
# Use the frozen production binary, compiled by the CPU-2 sequence.
test -x src/clique_fast
/usr/bin/time -v -o logs/full_odd.time src/clique_fast data/costas_13.txt 12 13000 logs/full_odd proof 0 0 1000000 2 1 1 >logs/full_odd.stdout 2>logs/full_odd.stderr
