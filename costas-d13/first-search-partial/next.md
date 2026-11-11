# FINISHED — partial result only

Read result.md for the final report. D(13) remains 11–12. No heavy process is
running and this six-hour allocation has ended. Do not execute the historical
launch instructions below without a new authorized allocation.

The independent C++ audits exclude the first 157 original symmetry roots.
The exact remaining graph has 11,580 arrays, in 1,459 D4 orbits. Its input is
`data/costas_13_remaining_after_extra.txt`; see the two prefix audits and
`logs/extended_partial_reduction13.json`. The independent stdlib checker is
provided; full Python execution of the large prefixes was not completed.

Historical working checkpoints follow (superseded):

# ACTIVE — 22:55 UTC

Primary serial search TIMEOUT at1,771,601,920 nodes,110 roots entered,
109 complete (last unfinished rootindex131). No12 witness or full exclusion.
**Prefix audit running under session37959** (`partial_queue.py`), one C++
process3threads. Its log logs/prefix13_complete.stderr has~852m checked states.
It must finish all109 before any reduction is asserted. Proof was moved to
certificates/excluded_initial_roots13.proof.gz. Exact duplicate old checkpoints
were deleted only after byte-prefix hash equality with this master; records
in logs/duplicate_checkpoint_cleanup.json. Folder~565MiB, free disk~16GiB.

**WATCHER session78124 is already running finish_primary.py**. It automatically
launches post_partial_search.py immediately after partial_reduction13.json is
written by the successful audit, if >=13min total remain. DO NOT launch a manual
duplicate! It then runs the validated3-thread clique_threaded on the exact
remaining catalogue, with adaptive cap<=25min and audit reserve. Full negative
is independently checked; positive witness stdlib checked. Only then target flag.
If necessary inspect session78124 and logs/reduced_target13.stderr/json.

Future FULL tail audits now use check_trace_parallel_stack.cpp / binary,
with explicit8MiB worker stacks (same logical verifier, tested full11 and bad
boundaries). This avoids depending on default worker stack sizes. Current
prefix verifier code/binary were NOT modified during its run. Their recorded
hashes remain correct. check_cpp_certificate.py dispatches full parallel audits
to the explicit-stack binary. finalize_report.py commands were updated.

Threaded search now writes per-root generator-status ledger .roots.json,
NOT a certificate by itself; useful if continuation times out. Search logic
unchanged, core9/11 proofs byte-identical to serial and independently checked.
No new13 bound has yet been certified. Deadline23:41:31UTC; all guards reserve
5min for final reporting, kill whole process groups on resource timeout.

When remaining target work/audit finishes, finalize_report.py supports ordinary
or chained no12-packing and positive12. If unresolved, state11<=D13<=12 and exact
scoped exclusions. Inspect/update result.md, certificate hashes, limits,
priorart/searchrecord. Optional neighbours only after primary and if time.
Final chat<=8lines. Keep one heavy process at a time; no installs/paid calls,
publication/external messages/outside-folder writes.

# NEXT IMPORTANT STEP — 22:35 UTC

Primary session41100 nearing softcap8700 (~22:37UTC), still >1.747b states,
root127, no target result yet. If full EXHAUSTED/SAT the parent audits normally.
If TIMEOUT, immediatelyrun **python3 partial_queue.py** under exec to audit all
completed roots in parallel. Then, after audit ends, if primary still unresolved
and remaining budget>=8min+5min final reserve, immediatelyrun
**python3 post_partial_search.py**. It now uses a validated three-thread root
search (`clique_threaded`) in ONE heavy process on the exact remaining graph.
All negative root pieces concatenate in canonical order; complete9/11 traces
were byte-identical to serial and independently checked, positive12 checked.
This can use remaining time much more effectively than replaying old states.
Cap is adaptive<=25min with time reserved for full independent C++ tail audit.
If both prefix and tail audits succeed it sets kindchained no12-packing,
handled byfinalize_report.py. Plain Python chain checker validates both proof
components and the exact data relation, no search imports. Never claim the
prepared/tested code itself establishes13. Primary unresolved as ofthis note.

Original global deadline23:41:31UTC. No orphan children after guard timeouts.
One heavy process at a time. C++ audit/search can use3threads in that process.
Final<=8lines and complete result.md. Check actual audit files before claiming.

# CURRENT — 22:24 UTC

Primary session41100 still running; >1.622b states at catalogue root112.
**Softcap is now8700 ->22:37UTC**, following actual order13 parallel audit
calibration (logs/parallel_target_benchmark.json):3m sampled nodes,3threads,
4.67185s including seeks, conservative1.86035x serial. This is PERFORMANCE ONLY,
not a certificate. Full independent C++ checker remains finalized sourcefa873...
three threads, one process, shared immutable graph, streaming gzip.
Original absolute deadline23:41:31UTC; final resource guards reserve5min.

On full EXHAUSTED/SAT live parent does automatic independent check and sets
logs/target_resolved.json only after success. On TIMEOUT: runpartial_queue.py
first (parallel prefix audit of ALL completed roots, including non-milestones).
Then prioritizepost_partial_search.py if enough time: adaptive cap<=25min from
remaining original budget, preserves audit time; exact induced graph verified
by independent stdlib check_chained13.py. It can yield kindchained no12-packing.
finalize_report.py supports the chained two-proof result and ordinary result.
No primary mathematical result has been certified yet.

Need finalize output even on partial: result.md exact scope, SHA256, commands,
limitations, priorart/searchrecord, errors. At most8lines final chat.
If target solved with time,neighbour_queue.py runs bounded decisions. Optional
python_target_prefix.py adds first-root stdlib execution if>=35min remain.
Do not claim full Python target execution; it is too slow unless actually done.

# Latest — 22:16 UTC

Primary still session41100, >1.546b states, rootindex103, not settled.
Softcap8400 ->22:32UTC; final deadline23:41:31UTC. All previous priorities hold.
Scoped parallel checker was refined to audit ALL completed roots after timeout,
not just the last20-root milestone: intermediate chunks are exact; last scoped
chunk permits unclaimed trailing bytes after its explicit root count and reports
actual consumed bytes. It was compared with stdlib Python/serial prefix cases;
a too-short final interval was rejected. Full parallel checker is unchanged.
`partial_queue.py` uses this scope if needed. Then prioritize post_partial_search
while time remains; it avoids full replay and has an adaptive cap<=25min, preserving time for audit.
`python_target_prefix.py` now supports either negative result kind if enough time.

# Latest — 22:12 UTC

Primary session41100 still active, `early_queue.py`. `logs/clique_early13.stderr`
>1.50b logical states, rootindex99. 80 roots completed through index93 at
1,471,858,108 states. No target certificate yet. Softcap8400 ->22:32UTC.
Parallel full/scoped independent C++ validators are finalized/tested (source
hash fa873... for full; graph shared read-only between3 threads, one process).
Driver auto-creates full boundary index and invokes parallel full checker if
primary EXHAUSTED. Check `logs/target_resolved.json` only after actual audit.
Full main parent remains session41100 and can be polled with write_stdin.

If primary TIMEOUT: run `python3 partial_queue.py` (parallel scoped audit).
Then if unresolved AND >=8min plus5min final reserve remain, prioritize
**python3 post_partial_search.py** before neighbours: it continues the exact
remaining induced graph without replaying billions of old states, cap<=25min.
The independently tested `check_chained13.py` checks that the reduced catalogue
is EXACTLY all remaining D4 orbits, using stdlib only. If reduced search completes
negative and passes independent C++ check, it writes target_resolved kind
**chained no 12-packing**; finalize_report.py now supports that two-proof result.
Its full pure-Python check calls the separate independent proof decoders and
never imports search code. If reduced search stays open, preserve original
partial result and make no global bound. No chained audit has yet run.

After primary settled (or all useful primary time used) run neighbour_queue.py
if time. Optional python_target_prefix.py (~15min) only when sufficient time;
for a chained result that script does NOT support the kind, so skip it or adapt
carefully. All final claims must match actual audit files.
Global deadline23:41:31UTC. Process-group guards kill children on resource stop.
Finalize with finalize_report.py, inspect result.md, add actual neighbours and
optional Python root check manually. Final<=8lines. One heavy process at a time.

# CURRENT — 21:50 UTC

Primary session **41100** still running `early_queue.py` -> `clique_early`.
Read `logs/clique_early13.stderr`; >1.264b states, no witness/full result yet.
60 roots completed through catalogue index71 at1,213,816,346 states.
Updated heuristic total1.37b states (not a bound). Original deadline23:41:31UTC.

IMPORTANT: independent full C++ audit is now PARALLEL, still ONE heavy process,
three threads, streaming gzip, ~100MB RAM. `check_trace_parallel.cpp` passed
full9/11 and strict bad-boundary/missing-root/opcode/gzip rejection tests.
Order11 took1.82357s versus4.14710 serial. Root-range metadata is UNTRUSTED;
all roots, exact byte consumption, CRCs, ENDPROOF/EOF independently checked.
The plain stdlib `check_clique_proof.py` is unchanged, no index required.
`check_cpp_certificate.py` auto-generates certificate boundaries for completed
primary proof and selects this backend. Thus existing live parent will use it.
Serial backend remains for other files unless --boundaries supplied explicitly.

Soft control **logs/early13.time-limit now8400** -> stop about22:32UTC.
This uses faster verification to allow extra search, within original6-hour cap.
Outer guard still11000 (23:15), not relevant before the soft stop.
On EXHAUSTED/SAT parent runs full independent check and sets target_resolved.
On TIMEOUT run **python3 partial_queue.py**: it now uses `check_prefix_parallel`
and the largest fully logged20-root milestone, writes explicit restricted scope.
This parallel scoped checker also passed independently compared prefix pilots.

`run_guarded.py` future runs now create isolated process groups and kill the
whole group on resource stop, so a C++ child of a Python driver cannot orphan.
Tested with sleeping dummy processes (no additional heavy computation).
The live search guard is older but its child is the direct C++ search, safe.

After primary audit succeeds, run `neighbour_queue.py` if time. Optional
`python_target_prefix.py` additionally checks first target root in pure Python
(~15min) only if >=25min+10min remain. Never claim it checked all target roots.
Finalize via `python3 finalize_report.py`; inspect, add exact checked neighbours
and any optional Python root audit manually. Final<=8lines. No paid calls,
installs, outside writes, publication, or external messages.

# Latest — 21:15 UTC

Active primary session41100, `early_queue.py`, child `clique_early`, logs
`logs/clique_early13.stderr`. Fresh search >885m logical states. First40 roots
completed through index50 at870,922,093 states. No target certificate yet.
Working runtime projection rose to1.236b states from the40-root pilot profile;
this is uncertain and not a result. Final-policy independent verifier speed
sample2.95305 seconds/million (`logs/early_verifier_order13_sample.json`).

Soft control `logs/early13.time-limit` remains7200, normal stop22:12 UTC.
Original absolute six-hour deadline23:41:31 UTC. Reserve full independent audit.
On EXHAUSTED/SAT, the parent performs the independent full check and only then
creates `logs/target_resolved.json`. On TIMEOUT, parent exits without an audit;
run `python3 partial_queue.py` to verify the completed roots and produce a
strictly scoped reduction (no global bound). Run `neighbour_queue.py` only after
one of those audits succeeds and if time remains. It performs30s decisions.
Finalize `python3 finalize_report.py`, inspect exact claims, add any checked
neighbour outcomes manually, ensure hashes/commands/limitations. Final<=8lines.

# Planning caution — 20:47 UTC

`logs/runtime_projection.json` extrapolates ~1.014 billion target states from
one cross-order root profile; it is only a heuristic, not a runtime guarantee.
Order13 has254 corner-containing canonical roots versus128 at order11, and the
pilot target sizes differ (full11 versus12-of13). Do not assume that estimate
will hold. Keep the original 22:12 soft stop and reserve a full independent audit.
Current production has passed570 million states; no witness or complete proof.

# Supplementary scripts prepared, not yet run

After the primary full audit OR restricted audit has completed, if time remains,
`python3 neighbour_queue.py` performs 30-second decisions at orders17,14,15,
starting from each paper upper bound. Every completed negative gets the full
independent C++ audit, and cheap cases also Python; witnesses get stdlib checks.
It stops five minutes before the absolute deadline. Results are written to
`logs/neighbour_results.json`; if run, incorporate exact checked outcomes into
result.md manually, keeping unknowns distinct. No neighbouring improvement has
yet been established. Prioritize the target and its certificate check.

# Latest milestone — 20:28 UTC

Production replay complete at 933.493 elapsed seconds; 369,819,647 old records.
Fresh work now exceeds 371 million logical states, current canonical root 27.
Active session41100; `early_queue.py`; log `logs/clique_early13.stderr`.
A completed result is not yet available. Normal soft stop ~22:12 UTC.
If TIMEOUT, run `python3 partial_queue.py` to independently audit all completed
roots and record an explicit restricted reduction; it makes no global bound.
If EXHAUSTED/SAT, existing queue runs the full independent check and creates
`logs/target_resolved.json`. Finalize with `python3 finalize_report.py`, inspect
result.md, add material late outcomes, hash final files, final reply <=8 lines.
Global deadline 23:41:31 UTC; leave time for the independent audit.

# Current execution — 20:13 UTC

Session **41100**, `early_queue.py`, production `clique_early`.
Trace/log prefix `logs/clique_early13`. Soft-control file
`logs/early13.time-limit`, 7200 seconds from ~20:12 UTC; global deadline
23:41:31 UTC. The preceding vector-only replay was stopped before fresh work;
its redundant trace was hash-compared with the retained checkpoint and removed.

Final production code: `clique_early.cpp` + `small_early.hpp` with flags
`-O3 -std=c++17 -DDISABLE_HOLE_MATCHING -DENABLE_SMALL_KERNEL -lz`.
It first tests a greedy color cut on small nodes, then the unchanged row/column
selection. Order-11 nodes remained exactly 1,678,389, independently checked;
order-13 pilot improved from ~93k to ~185k nodes/s. This is the final chosen
implementation; avoid further replay overhead unless fixing a real error.

Optional partial-root independent checkers are available in case full search
does not finish: `check_root_prefix` (C++) and `check_clique_prefix.py` (stdlib).
They require an explicit positive root count and only claim that restricted
scope, deliberately ignoring later trace data. Tested agreeing on five order-9
roots. Neither can establish D(13) without coverage of all roots. Full checker
remains `check_trace`; production queue invokes it on EXHAUSTED only.

# Current continuation checkpoint — 20:10 UTC

Original deadline: 2026-11-10 23:41:31 UTC. Target still open.
Active exec session **45770**, parent `vector_queue.py`, guarded child
`./clique_vector data/costas_13.txt 12 7200 logs/clique_vector13 resume logs/clique_continue13.proof.gz logs/vector13.time-limit`.
Read `logs/clique_vector13.stderr`. Soft elapsed limit is dynamically read from
`logs/vector13.time-limit`, currently 7200 seconds (normal stop about 22:10 UTC).
Hard guard 11000s. Parent independently checks a completed negative in C++ and
creates `logs/target_resolved.json` only after it passes. Pure Python full check
runs only if measured projection fits remaining wall budget.

Source is `clique_vector.cpp` + `small_vector.hpp`; frozen copies under logs.
No matching/recolour heuristic in target; small sorted-vector representation
preserves the exact original search. Full pilot traces 9/11 and first 3,473,407
order-13 records matched byte-for-byte. It resumes a valid 369,819,647-node
prefix, including the first trial. Replay counts are not fresh nodes.
Check `finalize_report.py` when ending; it now reads vector continuation result.
Do not claim D(13) without complete independent audit.

The independent C++ verifier `check_trace.cpp` uses cell-incidence graph,
first-fit color decoding, and bounded stack arrays for small candidate sets.
Complete 9/11/repair pilot certificates and adverse traces tested. Order-13
performance sample ~2.83 seconds per million states. Separate stdlib Python
checker `check_clique_proof.py` is provided and full smaller pilots passed;
full order-13 Python execution is unlikely to fit and must not be claimed.

Previous checkpoint (superseded where noted):

# Working checkpoint (English)

Started 2026-11-10 17:41:31 UTC; absolute six-hour deadline 23:41:31 UTC.
Write only in this folder. One heavy computation at a time. Folder <1 GiB,
stop if free disk <3 GiB. No installs, paid calls, external messages, publication.

At 19:15 UTC the target is **not settled**. Published interval remains 11–12.
The first 25-minute clique run ended with TIMEOUT at 110,379,008 nodes, five
canonical roots completed and the sixth unfinished. `continue_queue.py` now
runs under exec session **57509**. It uses `./clique_resume`, log
`logs/clique_continue13.stderr`, combined trace `logs/clique_continue13.proof.gz`.
Trace replay finished at 364 seconds (110,379,007 old records); fresh search
has exceeded 114 million logical nodes at catalogue root 6.

The soft elapsed-time cap is read from **logs/continue13.time-limit**, initially
9000 seconds (about 21:38 UTC). It can be increased while the run is active,
e.g. to 10800 or 12600, if the remaining search and independent validation fit.
The outer hard guard is 13200 seconds, ending about 22:48 UTC; the global
deadline remains 23:41:31. Leave enough time for the complete independent check.
The queue checks a positive witness with stdlib Python, or an exhausted full
trace with the independent C++ verifier, and creates `logs/target_resolved.json`
only after that check. It additionally runs the pure-Python full verifier if
its measured pilot projection fits the remaining wall budget. Otherwise the
final report must explicitly distinguish the full C++ check from Python pilots.

The source and executable of the first trial were saved as
`logs/clique_long13.source.cpp` and `logs/clique_long13.executable`. The live
`clique.cpp` was subsequently extended with trace-guided continuation and greedy
lower witnesses; `clique_resume` is its build with DISABLE_HOLE_MATCHING.
Continuation command, using a new output prefix:

```
./clique_resume data/costas_13.txt 12 SECONDS logs/resume13 resume logs/clique_long13.proof.gz
```

It replays recorded color advice and starts appending at the first unrecorded
node. It currently requires ordinary traces (no Hall opcodes). Resume was tested
by truncating the order-9 trace at 100 nodes: the decompressed original full
trace was restored exactly and the independent checker accepted it.

Both latest checkers have now checked the complete order-11 certificate:
Python 63.04 seconds; optimized independent C++ 6.64 seconds for 1,678,389 nodes.
The C++ verifier is separate source `check_trace.cpp`: sorted-vector candidate
sets, graph built by cell incidence, first-fit vector decoding, strict case
coverage and ENDPROOF checks. It imports/includes no search code. Small valid,
resumed and malformed traces were also checked. A complete C++ search without
a complete independent check must not be reported as settled. All SAT trials
returned UNKNOWN. An explicitly interim `result.md` exists and must be replaced
or clearly finalized when the research ends.

Verified files: full-order exclusion traces 5, 7, 9, 11; witnesses for full 10,
full 12, and 12-arrays at 14 and 17; a checked order-13 10-witness from DLS.
These reproduce known bounds and do not settle 13. Matching-bound pilot gave a
checked Hall obstruction but very few cuts; omitted in long run. The catalogue
is all 12,828 distinct order-13 arrays, including every D4 variant, from Beard's
searched ZIP. Source completeness is external, discussed in `method.md`.

Important resources: `progress.md`, `method.md`, `sources/search-record.md`,
`sources/catalogue_provenance.json`. Final requested output is `result.md`, with
exact claims, method, certificate hashes, checker commands, limitations, prior
art, already-solved search record. Final chat reply at most 8 lines.
