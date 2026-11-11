#!/bin/bash
set -euo pipefail
cd "$HOME/costas-verify"
./independent_v2 data/costas_9.txt 9 300 logs/v2_n9_no9 0
./independent_v2 data/costas_9.txt 8 300 logs/v2_n9_yes8 0
./independent_v2 data/costas_10.txt 10 300 logs/v2_n10_yes10 0
./independent_v2 data/costas_11.txt 11 1800 logs/v2_n11_no11 0
./independent_v2 data/costas_12.txt 12 300 logs/v2_n12_yes12 0
./independent_v2 data/costas_13.txt 12 12000 logs/v2_n13_prefix 0
