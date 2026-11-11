# Research progress

All times UTC. Started 2026-11-10 17:41 (2026-11-11 local).

- 17:43: Read scout A01 and the full saved Frank–Dinitz manuscript. Confirmed cell-disjointness and target 11 versus 12. Found SAT 2021 work and inspected its publisher abstract. Free disk initially 5.2 GiB. No paid calls or external messages.
- 17:49: Prior-art search located no resolution. CP-SAT pilot: full order 10 found in 4.25 seconds and independently checked; full orders 5/7 excluded by solver in 0.01/0.08 seconds; orders 9/11/12 timed out at 20 seconds. A general 13/12 trial has a five-minute cap. Four-rotation construction reproduces 12-array witnesses at 14 and 17, independently checked; no three-orbit construction at 13/15. Source table lists an impossible 6,239 edges at order 26; direct rebuilding gives 624. Downloaded Beard 2007 preprint for enumeration provenance. Current folder remains small; free disk was 7.5 GiB at last check.
- 17:52: CP-SAT 13/12 reached its 300-second cap with UNKNOWN. Bitset clique pilots: full 9 excluded in 0.024 seconds; full 11 excluded in 29.95 seconds (1,678,389 nodes); full 10 and 12 witnesses found in under 0.003 seconds. Separate stdlib Python checker confirmed the complete exclusion traces for orders 5, 7, 9. An initial 60-second general 13/12 clique trial is running. Added both row and column cell partitions to its bounds.
- 17:59: Independent stdlib checker confirmed full order-11 exclusion (all 555 symmetry roots, 1,678,389 nodes), in 190.39 seconds. Optimized C++ repeats the same exclusion in 12.95 seconds. Order-13 60-second trial timed out within its first root after 1,359,872 nodes. This is not an exclusion. Testing explicit hole-permutation formulation of 13/12 with one-thread CP-SAT, five-minute cap. Proof generation has disk and 800-MiB trace caps; guarded runs also monitor total folder size and write status at least every half hour.
- 18:05: Hole CP-SAT trial reached UNKNOWN at 300 seconds. CNF encoding independently reconstructed and checked (192,901 variables; 550,923 clauses). Existing drat-trim found on PATH; a full-order-5 Kissat UNSAT proof passed it. Starting ten-minute Kissat trial on order 13 with gzip DRAT output. Restricted construction checks found no witness: lifting order-12 arrays gives only 135 candidates and no 12-clique; extending two rotation orbits examines 658 bases with at most four extension candidates, and none has even an 11-extension. These are restricted searches, not general exclusions.
- 18:44: General trials remain undecided: sequential-CNF Kissat 600s UNKNOWN; binary-CNF Kissat 180s UNKNOWN; direct-conflict Kissat 180s UNKNOWN. The direct CNF (53,012,310 clauses, 25,825 variables, 141 MiB gzip) passed a complete independent encoding audit. Incomplete DRAT traces were hashed and removed. A 25-minute complete clique trial began 18:34:10, currently ~54.5 million nodes in canonical root 2; no global exclusion or 12-witness yet. Matching-bound pilot: 75 cuts / 5,210,112 nodes; a recorded Hall obstruction passed an independent check. Built a trace-guided continuation and tested it by truncating and restoring order 9: the decompressed full trace was restored exactly and independently verified. Current folder is ~210 MiB; disk guard remains active. No paid calls, installs, publications, or external messages.
- 19:15: First long trial ended at 1,500s and 110,379,008 nodes (five roots completed; sixth unfinished). Latest independent Python checker confirmed the full order-11 trace in 63.04s; additional independent C++ checker in 6.64s. Continuation started 19:07:57 with a 9000s soft cap and 13200s hard guard, adjustable through logs/continue13.time-limit. Replayed the retained prefix in 364.4s; fresh search is now past 114 million logical nodes. Explicitly interim result.md contains inputs, hashes, checker commands, limitations and prior-art record. Target still unresolved.

- 2026-11-10 17:59:02 UTC: cpsat_holes_13_12: started; one heavy process

- 2026-11-10 18:04:03 UTC: cpsat_holes_13_12: ended: finished; return code 0; elapsed 301.6s

- 2026-11-10 18:05:25 UTC: kissat_holes_13_sym: started; one heavy process

- 2026-11-10 18:15:27 UTC: kissat_holes_13_sym: ended: finished; return code 0; elapsed 601.3s

- 2026-11-10 18:21:02 UTC: kissat_binary_13: started; one heavy process

- 2026-11-10 18:24:03 UTC: kissat_binary_13: ended: finished; return code 0; elapsed 181.0s

- 2026-11-10 18:25:04 UTC: clique_match_13_trial: started; one heavy process

- 2026-11-10 18:26:07 UTC: clique_match_13_trial: ended: finished; return code 0; elapsed 62.4s

- 2026-11-10 18:29:54 UTC: pairwise_gen13: started; one heavy process

- 2026-11-10 18:30:06 UTC: pairwise_gen13: ended: finished; return code 0; elapsed 12.1s

- 2026-11-10 18:30:06 UTC: pairwise_encoding13: started; one heavy process

- 2026-11-10 18:31:06 UTC: pairwise_encoding13: ended: finished; return code 0; elapsed 60.3s

- 2026-11-10 18:31:07 UTC: kissat_direct13: started; one heavy process

- 2026-11-10 18:34:10 UTC: kissat_direct13: ended: finished; return code 0; elapsed 183.1s

- 2026-11-10 18:34:10 UTC: clique_long13: started; one heavy process

- 2026-11-10 18:59:12 UTC: clique_long13: ended: finished; return code 0; elapsed 1501.9s

- 2026-11-10 19:00:09 UTC: cpp_check11_latest: started; one heavy process

- 2026-11-10 19:00:19 UTC: cpp_check11_latest: ended: finished; return code 0; elapsed 10.1s

- 2026-11-10 19:00:19 UTC: python_check11_latest: started; one heavy process

- 2026-11-10 19:01:24 UTC: python_check11_latest: ended: finished; return code 0; elapsed 64.9s

- 2026-11-10 19:07:57 UTC: clique_continue13: started; one heavy process

- 2026-11-10 19:37:57 UTC: clique_continue13: running for 1800s; folder 312.6 MiB; free disk 16.5 GiB

- 2026-11-10 20:07:57 UTC: clique_continue13: running for 3601s; folder 371.7 MiB; free disk 16.4 GiB

- 2026-11-10 20:09:32 UTC: clique_continue13: ended: finished; return code 0; elapsed 3695.1s

- 2026-11-10 20:09:42 UTC: clique_vector13: started; one heavy process

- 2026-11-10 20:10:03 UTC: Switched normally checkpointed target continuation at 369,819,647 trace records to vector representation. Full order-9/order-11 decompressed traces and a 3,473,407-record order-13 prefix are identical. Order-13 sample speed improved from 11.2984 to 9.07942 seconds per 1,048,576 nodes. Separate C++ verifier improved from 5.89523 to 2.83030 seconds per million; complete pilot and rejection checks passed. Target still open.

- 2026-11-10 20:11:53 UTC: clique_vector13: ended: finished; return code 0; elapsed 130.9s

- 2026-11-10 20:12:13 UTC: Final production optimization: canonical greedy color cut before row-score computation on small candidates. No new pruning rule; complete order-11 certificate independently accepted, same 1,678,389 nodes. Order-13 fresh pilot: 5,554,176 nodes / 30.0643 seconds versus original ~93k/s. Replay-only vector trial stopped; original 369,819,647-node checkpoint retained.

- 2026-11-10 20:12:13 UTC: clique_early13: started; one heavy process

- 2026-11-10 20:17:47 UTC: Supplementary 30-second target-13 (full Latin square) pilot also timed out, 3,571,712 nodes, second root unfinished. It supplies no upper-bound certificate. Main target-12 replay resumed; no extra heavy process remains.

- 2026-11-10 20:28:12 UTC: Production replay complete: 369,819,647 saved records in 933.493 elapsed seconds (including 30-second supplementary pause). Fresh target-12 search resumed, ~185k nodes/s. Full target remains open.

- 2026-11-10 20:42:15 UTC: clique_early13: running for 1802s; folder 541.3 MiB; free disk 16.2 GiB

- 2026-11-10 21:12:15 UTC: clique_early13: running for 3602s; folder 593.1 MiB; free disk 16.1 GiB

- 2026-11-10 21:15:41 UTC: Search completed 40 canonical roots through catalogue index50, 870,922,093 states. Current >885m. Cross-order planning projection rose from1.014b to1.236b states; uncertain, not a bound. Final advice-policy verifier sample2.95305 seconds/million. Still no witness/full exclusion; retain22:12 soft stop, then independent full or scoped audit.

- 2026-11-10 21:42:15 UTC: clique_early13: running for 5402s; folder 645.8 MiB; free disk 16.0 GiB

- 2026-11-10 21:45:58 UTC: Parallel independent verifier validated on complete orders9/11 and malformed metadata/trace cases. It uses three threads in ONE heavy process, bounded gzip reads, shared/copy input graphs, and independently verifies every prescribed root in each range plus global root coverage, stream CRCs, ENDPROOF and EOF. Order11:1.82357s versus4.14710s serial. Search itself unchanged; no replay. Primary full audit driver now selects this backend and records boundary/source hashes.

- 2026-11-10 21:48:51 UTC: Parallel scoped verifier also agrees with serial C++ and stdlib Python on smaller complete root prefixes. Extended search soft cap from7200 to8400 elapsed seconds (~22:32 UTC), using the measured audit speedup while retaining ample time inside the original23:41:31 six-hour deadline. Still one heavy process; search itself remains single-threaded.

- 2026-11-10 21:49:48 UTC: guard_group_selfcheck: started; one heavy process

- 2026-11-10 21:49:50 UTC: guard_group_selfcheck: ended: wall_time_limit; return code -15; elapsed 2.0s

- 2026-11-10 21:50:45 UTC: 60-root completed milestone1,213,816,346 states through index71. Heuristic final-state projection1.37b remains uncertain. Resource-guard selftest used only sleeping dummy processes; it confirmed group-wide termination, not an extra heavy computation.

- 2026-11-10 22:12:16 UTC: clique_early13: running for 7203s; folder 698.7 MiB; free disk 15.9 GiB

- 2026-11-10 22:12:31 UTC: 80 canonical roots completed through index93 at1,471,858,108 states; current>1.50b, still no witness/full exclusion. Prepared stdlib exact reduction/chain checker and a bounded post-partial continuation in case full search times out. Those scripts are not a claim of proof. The reduction checker accepted an independently generated one-orbit filter and rejected omission of an eligible array.

- 2026-11-10 22:24:13 UTC: Actual order13 parallel performance sample (NOT a certificate):3m nodes,3threads,4.67185s including seeks; conservative speedup1.86035 versus serial sample. Changed search soft cap8400->8700 (~22:37UTC), retaining ~64min before original23:41:31 deadline for independent audit/report. Source search unchanged.

- 2026-11-10 22:36:22 UTC: Threaded reduced-continuation search validated: complete9/11 traces match serial byte-for-byte, independent C++ audits passed; full12 witness passed stdlib checker. Order11 search3.77683s versus8.77556s serial. One process, three threads, graph shared read-only. post_partial_search.py now selects it if required, preserving final audit time.

- 2026-11-10 22:37:17 UTC: clique_early13: ended: finished; return code 0; elapsed 8703.9s

- 2026-11-10 22:38:05 UTC: prefix13_complete: started; one heavy process

- 2026-11-10 23:08:07 UTC: prefix13_complete: running for 1801s; folder 564.7 MiB; free disk 15.9 GiB

- 2026-11-10 23:15:12 UTC: prefix13_complete: ended: finished; return code 0; elapsed 2226.5s

- 2026-11-10 23:15:14 UTC: reduced_target13: started; one heavy process

- 2026-11-10 23:18:17 UTC: guard_deadline_selfcheck: started; one heavy process

- 2026-11-10 23:18:17 UTC: guard_deadline_selfcheck: absolute deadline adjusted within original six-hour budget: 2026-11-10T23:18:17.960416+00:00

- 2026-11-10 23:18:19 UTC: guard_deadline_selfcheck: ended: wall_time_limit; return code -15; elapsed 2.1s

- 2026-11-10 23:27:08 UTC: reduced_target13: ended: finished; return code 0; elapsed 713.6s

- 2026-11-10 23:29:04 UTC: Remaining-graph soft cap712->848 seconds, within its pre-existing852-second hard guard. Future full independent audit absolute deadline23:39UTC, still before original six-hour23:41:31 limit; all disk/memory/group-stop guards remain active. Draft report has been generated/reviewed to preserve finalization time. No global13 result yet.

- 2026-11-10 23:32:52 UTC: check_extra_remaining13: started; one heavy process

- 2026-11-10 23:32:52 UTC: check_extra_remaining13: absolute deadline adjusted within original six-hour budget: 2026-11-10T23:39:00+00:00

- 2026-11-10 23:37:50 UTC: Correction to the 23:29 cap-change note: the reduced search had already stopped before that update. Its actual result is TIMEOUT after 712.025 seconds and 338,098,665 nodes, not an 848-second run. Final independent audit covers only 48 completed reduced roots; no global D(13) conclusion is claimed.

- 2026-11-10 23:38:14 UTC: check_extra_remaining13: ended: finished; return code 0; elapsed 322.0s

- 2026-11-10 23:39:12 UTC: FINISHED within the original six-hour budget. Second independent scoped audit passed: 48 reduced roots, 298,797,712 nodes, 320.77 seconds. Combined certified exclusion: first157 original root families, original representative indices through195; exact remaining catalogue11,580 arrays/1,459 orbits. D(13) remains11–12. Final result.md generated and reviewed; no heavy computation remains. Folder approximately712 MiB, free disk approximately16 GiB.
