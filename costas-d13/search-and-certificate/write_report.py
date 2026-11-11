#!/usr/bin/env python3
"""Render the final report from completed, checked measurements only."""
import datetime,hashlib,json
from pathlib import Path

j=lambda p:json.loads(Path(p).read_text())
s=j('logs/isolated_benchmark_summary.json');m=j('certificates/order13_manifest.json');t=j('logs/final_timing.json')
assert m['status']=='EXHAUSTED_INDEPENDENTLY_VERIFIED'
assert j('logs/isolated_status.json')['status']=='COMPLETE'
assert j('logs/full_check13.json')['verified']
assert m['nodes']==2249110973 and m['roots']==1616

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
files=['new_9_8.witness.json','new_9_9.proof.gz','new_10_10.witness.json','new_11_11.proof.gz','new_12_12.witness.json','new_13_11.witness.json','no_12_order13.proof.gz']
hashes={name:sha(Path('certificates')/name) for name in files}
assert hashes['no_12_order13.proof.gz']==m['proof_sha256']
assert hashes['new_11_11.proof.gz']=='365c1ac658dcfe36fd7700e4038c619c15c4c284c33fdbd3efdcf8d7ba571d26'
Path('certificates/SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
rows=s['order13_sample'];held=rows[1:]
held_gain=sum(r['old_seconds'] for r in held)/sum(r['new_seconds'] for r in held)
cpu_gain=t['iso_old_13']['cpu_seconds']/t['iso_new_13']['cpu_seconds']
peak=max(m['root_records'],key=lambda r:r['seconds'])
f=s['full_estimates'];old_cpu_hours=m['nodes']*t['iso_old_13']['cpu_seconds']/s['order13_totals']['nodes']/3600
metrics=dict(held_out_gain=held_gain,cpu_sample_gain=cpu_gain,old_estimated_cpu_hours=old_cpu_hours,
             new_search_cpu_hours=t['search_cpu_hours'],new_search_thread_hours=f['new_measured_core_hours'],
             max_root_ordinal=peak['ordinal'],max_root_seconds=peak['seconds'],
             mac_rate_only_hours=m['nodes']/185000/3600,
             estimated_four_core_search_minutes=f['new_measured_core_hours']*60/4)
Path('logs/final_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
lines=[]
lines.append('# Exact Costas search acceleration — completed 11 November 2026 UTC\n')
lines.append(f'The new solver is **{s["order13_totals"]["speedup"]:.2f}× faster** than the frozen `clique_early` baseline on the declared order-13 sample, and **{s["order11_medians"]["speedup"]:.2f}× faster** on the full order-11 exclusion (ratio of medians). The complete search and independent verification establish **D(13)=11, conditional on completeness of the supplied Beard catalogue**: a fresh 11-packing is checked directly, and every possible 12-packing in that catalogue is excluded.\n')
lines.append('The catalogue is an external completeness input. Every listed array, its Costas property, uniqueness and D4 closure were independently validated; exhaustive enumeration of all order-13 permutations was not repeated. Provenance is in `data/catalogue_provenance.json`; the order-13 input SHA-256 is `'+m['catalogue_sha256']+'`. This is a separate VM execution and a new local graph kernel, sharing the baseline’s catalogue, symmetry reduction and branch strategy.\n')
lines.append('The implementation is `src/clique_fast.cpp` with `src/local_fast.hpp`. For candidate sets of at most 512 vertices it constructs a fixed local induced graph in eight 64-bit words and reuses it throughout the subtree. Local cell-incidence masks construct a vertex’s neighbours as the complement of all arrays sharing one of its cells, replacing pairwise gathers into the global graph. Row and column partitions use these masks and hardware popcounts; column masks are the transpose of row masks.\n')
lines.append('The branching score remains the number of vertices in colour classes numbered at least `need`. For a full packing there are at most `need` supported cells per row/column; for a one-hole packing there are at most `need+1`. Its score is therefore the smallest class size or the sum of the two smallest, calculated without sorting every class-size list. The general case retains sorting. An early canonical greedy colouring can close a node before row/column scoring. These operations retain all open branch choices and their order; already-closed nodes can emit different valid advice bytes. No stronger pruning rule or vertex reordering was introduced.\n')
lines.append('Correctness follows from four facts. The local cell-union neighbourhood is exactly disjointness. Cell classes and greedy classes are independent sets, so their colour counts bound a clique. Reverse-prefix branching visits the unique greatest vertex of every possible completion, and a prefix with fewer than `need` colours cannot complete it. Finally, the least catalogue index over all eight common board images of a packing yields a canonical root whose other members have larger indices and representatives at least that root. Cardinality pruning is immediate. Timeouts carry no exclusion status. The complete arguments, including trace composition, are in [correctness.md](correctness.md).\n')
lines.append('Pairwise-gathered local graphs were an unsuccessful pilot (26.02s for order 11). Cell-incidence construction and a larger reusable universe worked better; 512 was selected using order 11 and order-13 root 0. Exploratory timings had differing concurrent loads and are retained in the logs; the comparisons below use the final controlled protocol.\n')
lines.append('All measured comparisons used the same AMD EPYC x86-64 VM, g++ 13.3.0, original catalogue order, symmetry roots and gzip trace output. Both builds used `-O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING`, linked with `-lz`; the new build adds `-DLOCAL_THRESHOLD=512`. `baseline/clique_early.cpp` and `small_early.hpp` are unchanged copies. `timed_baseline.cpp` adds root controls and logging only; see `logs/baseline_controls.diff`. Source/binary hashes are in `logs/final_source_hashes.json`.\n')
lines.append('Final timings are sequential runs on CPU 3, after our searches, audits and transfer ended. Two foreign nice-10 `scan` jobs on CPU 2 were left untouched. Before/after process snapshots and CPU accounting are retained; CPU 3 recorded no nice ticks or steal time during the comparison. The sample’s CPU-time gain is '+f'{cpu_gain:.2f}×'+', close to its wall-time gain. Search seconds exclude input/graph setup, following the baseline timer; `/usr/bin/time -v` files retain whole-process wall/CPU time and memory.\n')
lines.append('The full order-11 exclusion visits all 555 canonical roots. Paired run order alternated; every run visited exactly 1,678,389 nodes.\n')
lines.append('| Repeat | Baseline seconds | New seconds |\n|---|---:|---:|')
for r in s['order11']:lines.append(f'| {r["repeat"]} | {r["old_seconds"]:.5f} | {r["new_seconds"]:.5f} |')
lines.append(f'| Median | {s["order11_medians"]["old_seconds"]:.5f} | {s["order11_medians"]["new_seconds"]:.5f} |\n')
lines.append('The fixed order-13 sample uses zero-based **canonical root ordinals**, with the original catalogue index shown separately. Root 0 was used for tuning; the other seven were held out. Both programs visited exactly the same nodes at every listed root.\n')
lines.append('| Root ordinal | Catalogue index | Nodes, each program | Old seconds | New seconds | Gain |\n|---:|---:|---:|---:|---:|---:|')
for r in rows:
 tiny=r['nodes']==1
 a='<0.001' if tiny else f'{r["old_seconds"]:.3f}'
 b='<0.001' if tiny else f'{r["new_seconds"]:.3f}'
 gain='—' if tiny else f'{r["speedup"]:.2f}×'
 lines.append(f'| {r["ordinal"]} | {r["vertex"]} | {r["nodes"]:,} | {a} | {b} | {gain} |')
z=s['order13_totals']
lines.append(f'| Total | | {z["nodes"]:,} | {z["old_seconds"]:.3f} | {z["new_seconds"]:.3f} | **{z["speedup"]:.2f}×** |\n')
lines.append(f'The seven held-out roots give {held_gain:.2f}× by total time. One-node microtimings carry no useful speedup interpretation. Raw data: `logs/isolated_benchmark_summary.json`, `iso_*_13.roots.jsonl`, `iso_*_13.time`, and `iso_*_11_*.json`.\n')
lines.append('The complete order-13 target-12 decision used two independent root shards on the allowed CPUs 2 and 3. Its first 40 roots exactly reproduced the user-supplied milestone of 870,922,093 states.\n')
lines.append('| Shard | Canonical roots | Nodes | Search seconds |\n|---|---:|---:|---:|')
for name in ['full_even','full_odd']:
 d=m['summaries'][name];lines.append(f'| {name.removeprefix("full_")} | {d["roots"]} | {d["nodes"]:,} | {d["seconds"]:.2f} |')
lines.append(f'| Total | {m["roots"]:,} | **{m["nodes"]:,}** | **{m["search_core_seconds"]:.2f}** |\n')
lines.append(f'That is **{f["new_measured_core_hours"]:.3f} pinned-thread wall core-hours**, or {t["search_cpu_hours"]:.3f} measured user+system CPU-hours. The staged experiment spanned {t["search_staggered_span_seconds"]/60:.2f} minutes from the first search start to the last finish because CPU 2 first ran the baseline sample; the maximum shard duration is {max(d["seconds"] for d in m["summaries"].values())/60:.2f} minutes.\n')
lines.append('Independent checking used the copied C++ verifier with only explicit modulo-root selection, root logging and `ENDROOTS` marker changes; node verification code is unchanged (`logs/checker_adapter.diff`). Its split-order-11 regression reproduced all 555 roots and 1,678,389 nodes. For order 13 it independently rebuilt the data and graph, decoded both entire forests, checked every required child and EOF, and signed all 808 roots in each scope. Each independently audited root index/node count matched its member’s CRC-checked decoded byte length; the full archive hash also matched. Thus the scopes certify the joined canonical-order stream, which is compatible with the unchanged full verifier. `logs/full_check13.json` and the final `certificates/order13_manifest.json` record success.\n')
lines.append(f'The audits used {t["verification_cpu_hours"]:.3f} CPU-hours. Their wall durations were 8734.01s and 8748.73s (about 2h26m elapsed), including later CPU-2 co-tenant contention. Only our two decoder affinities were balanced within CPUs 2–3; external processes were unchanged. These audit wall times are not used to estimate search speed. All detached job PIDs and operational changes are recorded in `logs/pids.md`.\n')
lines.append('Before completion, the eight-root sample gave 2.261 billion states with log-linear interpolation and 2.656 billion with linear interpolation. A declared wider planning scenario was 1.696–3.320 billion, with no confidence-interval or bound interpretation. Relative to the actual 2.249 billion, the logarithmic estimate was 0.54% high and the linear estimate was 18.1% high. The user-supplied earlier 1.0–1.24 billion forecast was optimistic. The original forecast, assumptions and timestamp are preserved in `logs/precompletion_forecast.json`; completion removes the state-count uncertainty for this instance.\n')
lines.append('Full baseline time is projected from the now-known work count and the sample’s weighted seconds per state. The scenario uses observed per-state extremes on the five roots with at least 100,000 states, expanded by 15%; it is a planning range with no statistical coverage guarantee.\n')
lines.append('| Full order-13 work | Core-hours | Basis |\n|---|---:|---|')
lines.append(f'| Baseline search | **{f["old_estimated_core_hours"]:.2f}**, scenario **{f["old_scenario_core_hours"][0]:.2f}–{f["old_scenario_core_hours"][1]:.2f}** | Same negative state tree; sample-time projection |')
lines.append(f'| New search | **{f["new_measured_core_hours"]:.3f}** | Measured single-thread search seconds summed over shards |')
lines.append(f'| Independent verification | {t["verification_cpu_hours"]:.3f} CPU-hours | Measured user+system CPU time; wall time affected by sharing |\n')
lines.append(f'The corresponding baseline CPU-time projection is {old_cpu_hours:.2f} CPU-hours. Using only the supplied Mac rate of 185k nodes/s gives {metrics["mac_rate_only_hours"]:.2f} Mac core-hours for this node count; no Mac search was run.\n')
lines.append(f'More **dedicated CPU cores would matter**: roots and their audits are independent. Ideal new-search time is about {metrics["estimated_four_core_search_minutes"]:.1f} minutes on four equally fast available cores, before scheduling/cache effects; scaling above two cores was not measured. The heaviest measured root took {peak["seconds"]:.1f}s, leaving substantial root-level parallelism. Verification now costs more CPU time than search, so extra cores help certification too. Peak search RSS was about 30 MiB per process and the global adjacency matrix is 20.6 MB; additional RAM capacity would not address the observed bottleneck.\n')
lines.append('Required regressions and certificates were all reproduced by the new solver.\n')
lines.append('| Order | Established regression | Independent checks |\n|---:|---|---|\n| 9 | Packing of 8 arrays plus complete no-9 proof: 2,036 nodes, 100 roots | Copied witness, C++ and stdlib Python checkers; own Python audit |\n| 10 | Packing of 10 arrays (full board) | Direct displacement/cell and catalogue-membership checker |\n| 11 | Complete no-11 proof: 1,678,389 nodes, 555 roots | Copied C++, copied stdlib Python, independently written own stdlib Python |\n| 12 | Packing of 12 arrays (full board) | Direct displacement/cell and catalogue-membership checker |\n| 13 | Packing of 11 arrays plus complete no-12 proof | Direct witness checker and full independent C++ replay |\n')
lines.append('The order-13 11-witness was found in 53.29s / 18,495,699 nodes. ASan+UBSan completed the full order-11 exclusion and a 15-second order-13 prefix without diagnostics. All 21 deliberately damaged-proof checks were rejected across the three decoders, including wrong cardinality cuts, missing nodes/markers, extra data, truncation and CRC damage. These test scopes are retained in the logs.\n')
lines.append('The complete certificate files are indexed below and in `certificates/SHA256.json`. The order-13 proof is 379,174,621 bytes compressed, with 2,249,110,981 decoded bytes (one per node plus `ENDPROOF`). Its root members were archived incrementally with a recovery map, keeping both workspaces below 500 MB.\n')
lines.append('| File under `certificates/` | SHA-256 |\n|---|---|')
for name in files:lines.append(f'| [{name}]({(Path("certificates")/name).resolve()}) | `{hashes[name]}` |')
lines.append('\nBuild/search commands and both root controls are in [README.md](README.md). For a simple full replay, compile the unchanged copied checker and run it on the supplied archive on the VM:\n')
lines.append('```sh\ng++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp -lz -o checkers/check_trace\ntaskset -c 3 checkers/check_trace data/costas_13.txt certificates/no_12_order13.proof.gz 12\npython3 checkers/check.py certificates/new_13_11.witness.json --catalogue data/costas_13.txt\n```\n')
lines.append('The completed two-scope audit is recorded by `finish_parallel.sh`, `stream_scope.py`, `checkers/check_roots.cpp`, and the saved per-root audit logs. Smaller complete proofs can also be checked with `checkers/check_clique_proof.py` or `checkers/audit_speed.py`. No search or full proof replay was run on the Mac; all scientific computation used the allowed VM cores.\n')
report='\n'.join(lines)
report=report.replace('(correctness.md)',f'({Path("correctness.md").resolve()})').replace('(README.md)',f'({Path("README.md").resolve()})')
report=report.replace('g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp', 'taskset -c 2 g++ -O3 -march=native -DNDEBUG -std=c++17 checkers/check_trace.cpp')
report=report.replace('python3 checkers/check.py certificates/new_13_11.witness.json', 'taskset -c 3 python3 checkers/check.py certificates/new_13_11.witness.json')
Path('speed.md').write_text(report)
print(json.dumps(metrics,indent=2))
