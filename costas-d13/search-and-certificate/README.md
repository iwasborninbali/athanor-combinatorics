# Exact Costas search acceleration

The final research report is `speed.md`; pruning and completeness arguments are in `correctness.md`. All computation uses `personal-vps:~/costas-speed/`, CPUs 2 and 3 only. No computation is launched in the neighbouring workspace.

## Build (VM, g++ 13 and existing zlib)

```sh
taskset -c 2 g++ -O3 -march=native -DNDEBUG -std=c++17 \
  -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING -DLOCAL_THRESHOLD=512 \
  src/clique_fast.cpp -lz -o src/clique_fast
taskset -c 2 g++ -O3 -march=native -DNDEBUG -std=c++17 \
  -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING \
  baseline/timed_baseline.cpp -lz -o baseline/clique_early_bench
taskset -c 2 g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp -lz -o checkers/check_trace
```

`baseline/clique_early.cpp` and `baseline/small_early.hpp` are unchanged copies. `baseline/timed_baseline.cpp` adds only root selection/logging controls. Every C++ node operation and bound of the baseline is retained.

## Single complete decision

```sh
taskset -c 2 src/clique_fast data/costas_11.txt 11 300 logs/example11 proof
taskset -c 2 checkers/check_trace data/costas_11.txt logs/example11.proof.gz 11
taskset -c 2 python3 checkers/check_clique_proof.py data/costas_11.txt logs/example11.proof.gz 11
taskset -c 2 python3 checkers/audit_speed.py data/costas_11.txt logs/example11.proof.gz 11
```

The arguments after `proof` are `slice_seconds root_begin root_end modulus residue per_root_traces`. Begin/end use canonical root **ordinals**, with the end excluded. `SPEED_ROOT_LIST=0,20,40,...` optionally selects specific ordinals. The summary status of a restricted run is only about that selected scope. Root traces omit a global footer. An ordinary unrestricted negative appends `ENDPROOF`; a positive or interrupted run does not.

## Two-core full order-13 search

Run each line as its own `setsid nohup ... >log 2>&1 < /dev/null &` job and record `$!`:

```sh
taskset -c 2 src/clique_fast data/costas_13.txt 12 13000 logs/full_even proof 0 0 1000000 2 0 1
taskset -c 3 src/clique_fast data/costas_13.txt 12 13000 logs/full_odd proof 0 0 1000000 2 1 1
```

After both have genuinely exhausted their scopes:

```sh
taskset -c 2 python3 merge_proof.py
taskset -c 2 checkers/check_trace data/costas_13.txt certificates/no_12_order13.proof.gz 12
```

`merge_proof.py` checks the root manifest, validates CRCs and one-byte opcode lengths, and joins the gzip members while preserving an fsynced recovery map. Redundant standalone members are removed after their exact bytes are embedded in the archive. It does not replace verification of the trees. The copied C++ checker above reads the resulting full stream unchanged. `checkers/audit_speed.py` is a separate stdlib-only implementation suitable for the smaller complete proofs. Positive witnesses are checked with `python3 checkers/check.py WITNESS --catalogue CATALOGUE`.

The actual detached jobs and PIDs are recorded in `logs/pids.md`. The scripts `pilot.sh`, `mask_pilot.sh`, `cells_pilot.sh`, and `fast_pilot.sh` document exploratory variants. Some slow variants were intentionally stopped; their traces are prefixes, not exclusion certificates. `benchmark_and_full.sh`, `validate_and_full.sh`, `finish_parallel.sh`, `extra_checks.sh`, and `isolated_inner.sh` are the final production/validation/benchmark sequences. `isolated_wait.py` schedules a final sequential comparison on CPU 3 after all other heavy programme jobs finish; background-load snapshots accompany the measurements. Earlier `finish.sh` was superseded while still waiting.

The frozen accelerated build is used for fresh `proof` runs and explicit root shards. The inherited legacy `resume` mode is outside this build's supported/tested interface; certificate replay uses the independent checkers. The complete order-13 result is recorded in `certificates/order13_manifest.json`, and certificate hashes are in `certificates/SHA256.json`.
