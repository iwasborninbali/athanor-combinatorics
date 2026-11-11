# Exact Costas search acceleration — completed 11 November 2026 UTC

The new solver is **3.28× faster** than the frozen `clique_early` baseline on the declared order-13 sample, and **2.60× faster** on the full order-11 exclusion (ratio of medians). The complete search and independent verification establish **D(13)=11, conditional on completeness of the supplied Beard catalogue**: a fresh 11-packing is checked directly, and every possible 12-packing in that catalogue is excluded.

The catalogue is an external completeness input. Every listed array, its Costas property, uniqueness and D4 closure were independently validated; exhaustive enumeration of all order-13 permutations was not repeated. Provenance is in `data/catalogue_provenance.json`; the order-13 input SHA-256 is `a8acc2805c86001250b9104dbf41c2804cdb5734823554ac5313141e9d93e17d`. This is a separate VM execution and a new local graph kernel, sharing the baseline’s catalogue, symmetry reduction and branch strategy.

The implementation is `src/clique_fast.cpp` with `src/local_fast.hpp`. For candidate sets of at most 512 vertices it constructs a fixed local induced graph in eight 64-bit words and reuses it throughout the subtree. Local cell-incidence masks construct a vertex’s neighbours as the complement of all arrays sharing one of its cells, replacing pairwise gathers into the global graph. Row and column partitions use these masks and hardware popcounts; column masks are the transpose of row masks.

The branching score remains the number of vertices in colour classes numbered at least `need`. For a full packing there are at most `need` supported cells per row/column; for a one-hole packing there are at most `need+1`. Its score is therefore the smallest class size or the sum of the two smallest, calculated without sorting every class-size list. The general case retains sorting. An early canonical greedy colouring can close a node before row/column scoring. These operations retain all open branch choices and their order; already-closed nodes can emit different valid advice bytes. No stronger pruning rule or vertex reordering was introduced.

Correctness follows from four facts. The local cell-union neighbourhood is exactly disjointness. Cell classes and greedy classes are independent sets, so their colour counts bound a clique. Reverse-prefix branching visits the unique greatest vertex of every possible completion, and a prefix with fewer than `need` colours cannot complete it. Finally, the least catalogue index over all eight common board images of a packing yields a canonical root whose other members have larger indices and representatives at least that root. Cardinality pruning is immediate. Timeouts carry no exclusion status. The complete arguments, including trace composition, are in [correctness.md](<workspace>/stalled-solve/a01-speed/correctness.md).

Pairwise-gathered local graphs were an unsuccessful pilot (26.02s for order 11). Cell-incidence construction and a larger reusable universe worked better; 512 was selected using order 11 and order-13 root 0. Exploratory timings had differing concurrent loads and are retained in the logs; the comparisons below use the final controlled protocol.

All measured comparisons used the same AMD EPYC x86-64 VM, g++ 13.3.0, original catalogue order, symmetry roots and gzip trace output. Both builds used `-O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING`, linked with `-lz`; the new build adds `-DLOCAL_THRESHOLD=512`. `baseline/clique_early.cpp` and `small_early.hpp` are unchanged copies. `timed_baseline.cpp` adds root controls and logging only; see `logs/baseline_controls.diff`. Source/binary hashes are in `logs/final_source_hashes.json`.

Final timings are sequential runs on CPU 3, after our searches, audits and transfer ended. Two foreign nice-10 `scan` jobs on CPU 2 were left untouched. Before/after process snapshots and CPU accounting are retained; CPU 3 recorded no nice ticks or steal time during the comparison. The sample’s CPU-time gain is 3.26×, close to its wall-time gain. Search seconds exclude input/graph setup, following the baseline timer; `/usr/bin/time -v` files retain whole-process wall/CPU time and memory.

The full order-11 exclusion visits all 555 canonical roots. Paired run order alternated; every run visited exactly 1,678,389 nodes.

| Repeat | Baseline seconds | New seconds |
|---|---:|---:|
| 1 | 16.89290 | 6.87509 |
| 2 | 15.14920 | 6.49175 |
| 3 | 17.00910 | 6.40190 |
| Median | 16.89290 | 6.49175 |

The fixed order-13 sample uses zero-based **canonical root ordinals**, with the original catalogue index shown separately. Root 0 was used for tuning; the other seven were held out. Both programs visited exactly the same nodes at every listed root.

| Root ordinal | Catalogue index | Nodes, each program | Old seconds | New seconds | Gain |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 24,129,882 | 286.532 | 81.500 | 3.52× |
| 20 | 31 | 23,179,947 | 275.125 | 79.450 | 3.46× |
| 40 | 51 | 16,813,835 | 175.921 | 51.347 | 3.43× |
| 80 | 96 | 15,220,246 | 161.514 | 60.755 | 2.66× |
| 160 | 200 | 4,343,907 | 49.633 | 16.086 | 3.09× |
| 320 | 592 | 1 | <0.001 | <0.001 | — |
| 640 | 956 | 1 | <0.001 | <0.001 | — |
| 1280 | 2216 | 1 | <0.001 | <0.001 | — |
| Total | | 83,687,820 | 948.729 | 289.140 | **3.28×** |

The seven held-out roots give 3.19× by total time. One-node microtimings carry no useful speedup interpretation. Raw data: `logs/isolated_benchmark_summary.json`, `iso_*_13.roots.jsonl`, `iso_*_13.time`, and `iso_*_11_*.json`.

The complete order-13 target-12 decision used two independent root shards on the allowed CPUs 2 and 3. Its first 40 roots exactly reproduced the user-supplied milestone of 870,922,093 states.

| Shard | Canonical roots | Nodes | Search seconds |
|---|---:|---:|---:|
| even | 808 | 1,113,548,025 | 4153.01 |
| odd | 808 | 1,135,562,948 | 4215.45 |
| Total | 1,616 | **2,249,110,973** | **8368.46** |

That is **2.325 pinned-thread wall core-hours**, or 2.307 measured user+system CPU-hours. The staged experiment spanned 84.51 minutes from the first search start to the last finish because CPU 2 first ran the baseline sample; the maximum shard duration is 70.26 minutes.

Independent checking used the copied C++ verifier with only explicit modulo-root selection, root logging and `ENDROOTS` marker changes; node verification code is unchanged (`logs/checker_adapter.diff`). Its split-order-11 regression reproduced all 555 roots and 1,678,389 nodes. For order 13 it independently rebuilt the data and graph, decoded both entire forests, checked every required child and EOF, and signed all 808 roots in each scope. Each independently audited root index/node count matched its member’s CRC-checked decoded byte length; the full archive hash also matched. Thus the scopes certify the joined canonical-order stream, which is compatible with the unchanged full verifier. `logs/full_check13.json` and the final `certificates/order13_manifest.json` record success.

The audits used 3.699 CPU-hours. Their wall durations were 8734.01s and 8748.73s (about 2h26m elapsed), including later CPU-2 co-tenant contention. Only our two decoder affinities were balanced within CPUs 2–3; external processes were unchanged. These audit wall times are not used to estimate search speed. All detached job PIDs and operational changes are recorded in `logs/pids.md`.

Before completion, the eight-root sample gave 2.261 billion states with log-linear interpolation and 2.656 billion with linear interpolation. A declared wider planning scenario was 1.696–3.320 billion, with no confidence-interval or bound interpretation. Relative to the actual 2.249 billion, the logarithmic estimate was 0.54% high and the linear estimate was 18.1% high. The user-supplied earlier 1.0–1.24 billion forecast was optimistic. The original forecast, assumptions and timestamp are preserved in `logs/precompletion_forecast.json`; completion removes the state-count uncertainty for this instance.

Full baseline time is projected from the now-known work count and the sample’s weighted seconds per state. The scenario uses observed per-state extremes on the five roots with at least 100,000 states, expanded by 15%; it is a planning range with no statistical coverage guarantee.

| Full order-13 work | Core-hours | Basis |
|---|---:|---|
| Baseline search | **7.08**, scenario **5.56–8.53** | Same negative state tree; sample-time projection |
| New search | **2.325** | Measured single-thread search seconds summed over shards |
| Independent verification | 3.699 CPU-hours | Measured user+system CPU time; wall time affected by sharing |

The corresponding baseline CPU-time projection is 7.02 CPU-hours. Using only the supplied Mac rate of 185k nodes/s gives 3.38 Mac core-hours for this node count; no Mac search was run.

More **dedicated CPU cores would matter**: roots and their audits are independent. Ideal new-search time is about 34.9 minutes on four equally fast available cores, before scheduling/cache effects; scaling above two cores was not measured. The heaviest measured root took 168.4s, leaving substantial root-level parallelism. Verification now costs more CPU time than search, so extra cores help certification too. Peak search RSS was about 30 MiB per process and the global adjacency matrix is 20.6 MB; additional RAM capacity would not address the observed bottleneck.

Required regressions and certificates were all reproduced by the new solver.

| Order | Established regression | Independent checks |
|---:|---|---|
| 9 | Packing of 8 arrays plus complete no-9 proof: 2,036 nodes, 100 roots | Copied witness, C++ and stdlib Python checkers; own Python audit |
| 10 | Packing of 10 arrays (full board) | Direct displacement/cell and catalogue-membership checker |
| 11 | Complete no-11 proof: 1,678,389 nodes, 555 roots | Copied C++, copied stdlib Python, independently written own stdlib Python |
| 12 | Packing of 12 arrays (full board) | Direct displacement/cell and catalogue-membership checker |
| 13 | Packing of 11 arrays plus complete no-12 proof | Direct witness checker and full independent C++ replay |

The order-13 11-witness was found in 53.29s / 18,495,699 nodes. ASan+UBSan completed the full order-11 exclusion and a 15-second order-13 prefix without diagnostics. All 21 deliberately damaged-proof checks were rejected across the three decoders, including wrong cardinality cuts, missing nodes/markers, extra data, truncation and CRC damage. These test scopes are retained in the logs.

The complete certificate files are indexed below and in `certificates/SHA256.json`. The order-13 proof is 379,174,621 bytes compressed, with 2,249,110,981 decoded bytes (one per node plus `ENDPROOF`). Its root members were archived incrementally with a recovery map, keeping both workspaces below 500 MB.

| File under `certificates/` | SHA-256 |
|---|---|
| [new_9_8.witness.json](<workspace>/stalled-solve/a01-speed/certificates/new_9_8.witness.json) | `60caaa12db1e14e5c7c34e4118213c06eaf1e1f43c496594d422fd3bb8e2cf95` |
| [new_9_9.proof.gz](<workspace>/stalled-solve/a01-speed/certificates/new_9_9.proof.gz) | `72c87ad4ca9ebed6c0dd44ebc75bba6086c77772905fac1317d4ad692a075d13` |
| [new_10_10.witness.json](<workspace>/stalled-solve/a01-speed/certificates/new_10_10.witness.json) | `6648b2b27131f1d645d11e9ee4dad270d838ee0f9dc80b117feb2ebc38c02e73` |
| [new_11_11.proof.gz](<workspace>/stalled-solve/a01-speed/certificates/new_11_11.proof.gz) | `365c1ac658dcfe36fd7700e4038c619c15c4c284c33fdbd3efdcf8d7ba571d26` |
| [new_12_12.witness.json](<workspace>/stalled-solve/a01-speed/certificates/new_12_12.witness.json) | `d7789de69cb3774280a31101a0d1162cf0be377aab557c3f32508a5c567a9702` |
| [new_13_11.witness.json](<workspace>/stalled-solve/a01-speed/certificates/new_13_11.witness.json) | `62de496e4cb0e6a014f1dd73020683bf2ab443595beb199b8f2d93a5c11e2f55` |
| [no_12_order13.proof.gz](<workspace>/stalled-solve/a01-speed/certificates/no_12_order13.proof.gz) | `95244d728ab911ce882b71f39d8edc794670daf5a7457bbf0ba26af43ad35d9e` |

Build/search commands and both root controls are in [README.md](<workspace>/stalled-solve/a01-speed/README.md). For a simple full replay, compile the unchanged copied checker and run it on the supplied archive on the VM:

```sh
taskset -c 2 g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp -lz -o checkers/check_trace
taskset -c 3 checkers/check_trace data/costas_13.txt certificates/no_12_order13.proof.gz 12
taskset -c 3 python3 checkers/check.py certificates/new_13_11.witness.json --catalogue data/costas_13.txt
```

The completed two-scope audit is recorded by `finish_parallel.sh`, `stream_scope.py`, `checkers/check_roots.cpp`, and the saved per-root audit logs. Smaller complete proofs can also be checked with `checkers/check_clique_proof.py` or `checkers/audit_speed.py`. No search or full proof replay was run on the Mac; all scientific computation used the allowed VM cores.
