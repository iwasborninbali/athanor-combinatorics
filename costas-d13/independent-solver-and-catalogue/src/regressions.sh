#!/bin/bash
set -euo pipefail
cd "$HOME/costas-verify"
./independent data/costas_9.txt 9 300 logs/n9_no9 0
./independent data/costas_9.txt 8 300 logs/n9_yes8 0
./independent data/costas_10.txt 10 300 logs/n10_yes10 0
./independent data/costas_11.txt 10 300 logs/n11_yes10 0
./independent data/costas_12.txt 12 300 logs/n12_yes12 0
./trace_audit data/costas_9.txt data/new_9_9.proof.gz 9 logs/trace9
./trace_audit data/costas_11.txt data/new_11_11.proof.gz 11 logs/trace11
./trace_audit data/costas_13.txt data/no_12_order13.proof.gz 12 logs/trace13
