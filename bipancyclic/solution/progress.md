# Progress

Started 2026-11-11 00:08 UTC. Deadline: approximately 06:08 UTC.

- 00:09 UTC: Prior-art check in progress. No later direct solution located in exact-title, minimum-edge, four-chord, excess, thesis, or OEIS web queries. Adjacent 2016 uniquely bipancyclic classification located. Source paper OCR read; its final excess notation and the endpoint at 16 need correction.
- Resources: initially 15 GiB free according to `df -h ~`; one heavy process at a time, no installations or paid calls.

All mathematical results remain provisional until independently checked.

- 00:13 UTC: First CP-SAT pilot found relaxed candidates, but independent original-graph DFS rejected N=44 and N=46 (zero-arc contractions had made some symbolic cycles non-simple). These are not witnesses. Added positive-length constraints on unused arc runs for each cycle selected to cover a target. No target value newly established yet.

- 00:15 UTC: Independently verified e(46)=4 with chords (0,5), (0,43), (1,38), (26,45). The original-graph enumerator finds 25 simple cycles and all required lengths.
- 00:19 UTC: Independently verified exclusion of four chords at N=48: 103 patterns, 110 valid parity/minimum-length cases, 35,466,805 arc assignments covered, 10,947,278 proof nodes; checker 24.22 seconds. Search 0.75 seconds. Pilot shows the full target feasible.
- 00:21 UTC: Generated all required negative certificates (k=2 at 16; k=3 at 28,30,32; k=4 at 48,50,...,64). The N>=62 cases close by the maximum 29 kernel cycles. Full independent certificate verification is running sequentially. All positive witnesses through 64 generated and independently checked. No final exclusion claim beyond the pilot until checker completes.

- 2026-11-11 00:27 UTC: COMPLETE. Independently verified all 31 positive witnesses and all 13 exclusion certificates, covering 347,904,236 arc assignments in 74,845,172 proof nodes. Checker time 183.30 seconds; final searches 5.09 logged seconds. e(46)=4, four chords have global maximum order 46, and e(N)=5 for every even 48<=N<=64. The exact small-order table is in result.md. Five corrupted-certificate/witness tests were rejected as expected. Proofs total 4,205,972 compressed bytes; folder about 8.7 MB; disk still about 15 GiB free.
