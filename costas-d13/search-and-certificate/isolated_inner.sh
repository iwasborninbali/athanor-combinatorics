#!/bin/bash
set -euo pipefail
cd "$HOME/costas-speed"
# Use the allowed core that avoided the observed CPU-2 contention.
taskset -p -c 3 $$ >logs/isolated_selected_cpu.txt
# Keep the final comparison free of the archive transfer.
while test -f logs/proof_transfer.active; do sleep 10; done
date -u >logs/isolated_started.txt
taskset -p $$ >logs/isolated_affinity.txt
cat /proc/stat >logs/isolated_cpu_before.txt
ps -eo pid,ppid,psr,ni,stat,pcpu,comm >logs/isolated_processes_before.txt
# No other computation from this programme is active during these runs.
for i in 1 2 3; do
 if test "$i" = 2; then labels=(new old); else labels=(old new); fi
 for label in "${labels[@]}"; do
  if test "$label" = old; then code=baseline/clique_early_bench; else code=src/clique_fast; fi
  /usr/bin/time -v -o "logs/iso_${label}_11_${i}.time" "$code" data/costas_11.txt 11 120 "logs/iso_${label}_11_${i}" proof >"logs/iso_${label}_11_${i}.stdout" 2>"logs/iso_${label}_11_${i}.stderr"
 done
done
for label in old new; do
 if test "$label" = old; then code=baseline/clique_early_bench; else code=src/clique_fast; fi
 SPEED_ROOT_LIST=0,20,40,80,160,320,640,1280 /usr/bin/time -v -o "logs/iso_${label}_13.time" "$code" data/costas_13.txt 12 1800 "logs/iso_${label}_13" proof 0 0 1000000 >"logs/iso_${label}_13.stdout" 2>"logs/iso_${label}_13.stderr"
done
cat /proc/stat >logs/isolated_cpu_after.txt
ps -eo pid,ppid,psr,ni,stat,pcpu,comm >logs/isolated_processes_after.txt
date -u >logs/isolated_finished.txt
python3 summarize_isolated.py >logs/isolated_summary.stdout
