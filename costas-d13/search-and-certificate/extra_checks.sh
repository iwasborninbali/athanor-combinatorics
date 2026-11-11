#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
while ! test -s logs/full_odd.json; do sleep 20; done
python3 checkers/audit_speed.py data/costas_9.txt certificates/new_9_9.proof.gz 9 >logs/own_check9.json
python3 checkers/audit_speed.py data/costas_11.txt logs/fast512_11.proof.gz 11 >logs/own_check11.json
python3 checkers/adversarial.py >logs/adversarial_checks.stdout
# Exercise the actual production source under memory and undefined-behaviour checking.
g++ -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=512 src/clique_fast.cpp -lz -o src/clique_sanitized
src/clique_sanitized data/costas_11.txt 11 300 logs/sanitized11 proof >logs/sanitized11.stdout 2>logs/sanitized11.stderr
src/clique_sanitized data/costas_13.txt 12 15 logs/sanitized13_prefix proof 0 0 1 >logs/sanitized13_prefix.stdout 2>logs/sanitized13_prefix.stderr
src/clique_fast data/costas_13.txt 11 600 certificates/new_13_11 proof >logs/new_13_11.stdout 2>logs/new_13_11.stderr
if test -f certificates/new_13_11.witness.json; then
 python3 checkers/check.py certificates/new_13_11.witness.json --catalogue data/costas_13.txt >logs/new_13_11_check.json
fi
