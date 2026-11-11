**Exact minimum excess of bipancyclic graphs through 64 vertices**

Research date: 2026-11-11. Vertices are labeled 0,...,N-1, with Hamilton edges (i,i+1 mod N). The graph is simple, undirected, and bipartite. The excess e(N) is the minimum number of edges minus N; equivalently it is the minimum number of added chords of a Hamilton cycle. N is even and at least 4.

The independently certified answer is **e(46)=4**. Moreover,

```
e(4) = 0
e(N) = 1  for N = 6,8
e(N) = 2  for N = 10,12,14
e(N) = 3  for even 16 <= N <= 26
e(N) = 4  for even 28 <= N <= 46
e(N) = 5  for even 48 <= N <= 64.
```

**46 is the largest order of any four-chord bipancyclic graph**, globally. Exclusions at 48,50,...,60 are checked exhaustively; every graph consisting of a Hamilton cycle and four chords has at most 29 simple cycles, which excludes every even N>=62. No monotonicity conjecture about the excess is used.

An explicit witness for 46 is

```
[(0,5), (0,43), (1,38), (26,45)].
```

The independent original-graph depth-first enumerator finds 25 simple cycles, including every even length 4,...,46. The lower bound is elementary: three chords give cycle-space dimension 4 and therefore at most 15 nonzero cycle-space elements, fewer than the 22 distinct cycles required at 46.

**Complete table.** The witness for every row is in `witnesses.json`; `witness_check.json` records cycle counts and an explicit vertex sequence for each required length.

| N | e(N) | Minimum edges | Relation to Wallis (2017) |
|---:|---:|---:|---|
| 4 | 0 | 4 | confirmed |
| 6 | 1 | 7 | confirmed |
| 8 | 1 | 9 | confirmed |
| 10 | 2 | 12 | confirmed |
| 12 | 2 | 14 | confirmed |
| 14 | 2 | 16 | confirmed |
| 16 | 3 | 19 | corrects Theorem 2 endpoint |
| 18 | 3 | 21 | confirmed |
| 20 | 3 | 23 | confirmed |
| 22 | 3 | 25 | confirmed |
| 24 | 3 | 27 | confirmed |
| 26 | 3 | 29 | confirmed |
| 28 | 4 | 32 | confirmed |
| 30 | 4 | 34 | confirmed |
| 32 | 4 | 36 | confirmed |
| 34 | 4 | 38 | confirmed |
| 36 | 4 | 40 | confirmed |
| 38 | 4 | 42 | confirmed |
| 40 | 4 | 44 | confirmed |
| 42 | 4 | 46 | confirmed |
| 44 | 4 | 48 | confirmed |
| 46 | 4 | 50 | extends located exact table |
| 48 | 5 | 53 | extends located exact table |
| 50 | 5 | 55 | extends located exact table |
| 52 | 5 | 57 | extends located exact table |
| 54 | 5 | 59 | extends located exact table |
| 56 | 5 | 61 | extends located exact table |
| 58 | 5 | 63 | extends located exact table |
| 60 | 5 | 65 | extends located exact table |
| 62 | 5 | 67 | extends located exact table |
| 64 | 5 | 69 | extends located exact table |

**Method and complete pattern coverage.** Every bipancyclic graph contains a Hamilton cycle, so fixing one loses no possible graph. With k chords, let m be the number of distinct chord endpoints. Suppress other Hamilton vertices, retaining the positive integer length a_i of each of the m circular arcs. Then 2<=m<=2k. Choose k distinct unordered pairs on these m vertices and require every vertex to be a chord endpoint. This directly includes every possible endpoint sharing; zero-length arcs are never needed.

The only pattern symmetry used is the dihedral group of the cyclic endpoint order. Rotation and reversal relabel both the chords and their circular arc variables and preserve feasibility. Each chord set is replaced by the lexicographically least image under all 2m rotations/reflections. Thus every original cyclic incidence pattern has a representative. No symmetry of arc lengths or colors is assumed beyond this relabeling and the global interchange of the two bipartite colors.

For four chords, the numbers of labeled chord sets before this quotient, for m=4,5,6,7,8, are respectively 15,135,330,315,105. The dihedral representative counts are respectively 4,17,38,27,17: **103 patterns** in all. For three and two chords the totals are 14 and 3. The independent checker generates these sets itself, without reading the search-side pattern files.

For each pattern, the search enumerates cycle-space elements and retains precisely the connected 2-regular edge subsets. The independent checker instead enumerates vertex-simple walks in the kernel multigraph, allowing two-edge cycles from parallel kernel edges. These correspond to ordinary simple cycles after expanding the positive arcs. The checker obtains maximum cycle counts 7,15,29 for two, three, four chords. For four chords, the maxima by m=4,...,8 are 20,22,24,26,29. All original simple cycles correspond to such kernel cycles, and all such kernel cycles expand without vertex repetition.

Fix the color of endpoint 0 to zero and enumerate every assignment of colors to the other endpoints, retaining exactly those for which every chord joins opposite colors. Adjacent circular endpoints of different colors require a_i odd, and those of equal colors require a_i even. Set their respective minimum lengths to 1 and 2. If a chord joins adjacent kernel vertices, raise the corresponding minimum arc length to 3 so the chord cannot duplicate a Hamilton edge. This condition is applied on both circular sides when m=2. All other chord spans automatically have odd length at least 3 in both directions. The selected chords are distinct by construction.

Writing a_i=b_i+2*x_i gives nonnegative integers x_i satisfying sum(x_i)=(N-sum(b_i))/2. This includes every valid positive arc assignment. Each simple cycle has half-length

```
constant + sum(x_i over a subset of arcs),
constant = (number of chords in the cycle + sum(b_i over its arcs))/2.
```

A pattern with fewer than N/2-1 cycles is excluded immediately. Otherwise an exhaustive branch-and-bound covers the full integer simplex of x assignments. After fixing a prefix of variables with remaining sum R, a cycle's still-unassigned 0/1 subset contributes exactly 0, exactly R, or lies in [0,R]. If some required half-length 2,...,N/2 is outside every cycle's interval, every completion is excluded. Otherwise the search branches over every possible value 0,...,R of the next variable. The last variable is determined by the sum. This is a complete finite enumeration with sound pruning, not a heuristic or a solver's unproved UNSAT flag.

**Exclusion certificates.** Gzipped `BPC1` files contain the exhaustive trees. The header records N, k, and the number of cases. The checker independently regenerates the entire ordered list of patterns, admissible colorings, minimum arc lengths, and cycle expressions. Each case begins with its pattern/color identifiers. A zero byte branches over every next-variable value; a byte h>=2 asserts that required half-length h is absent throughout the current simplex. The checker verifies that assertion against every independently derived cycle expression. It also checks complete child coverage, counts the represented integer assignments using binomial coefficients, and rejects missing cases, truncation, unsound leaves, and trailing data. At 62 and 64 the case list is empty because the independently enumerated 29-cycle bound already suffices.

| Chords excluded | N | Cases | Arc assignments covered | Proof nodes |
|---:|---:|---:|---:|---:|
| 2 | 16 | 2 | 112 | 110 |
| 3 | 28 | 10 | 22,386 | 13,844 |
| 3 | 30 | 8 | 29,939 | 16,780 |
| 3 | 32 | 4 | 21,672 | 8,536 |
| 4 | 48 | 110 | 35,466,805 | 10,947,278 |
| 4 | 50 | 88 | 42,685,654 | 11,429,809 |
| 4 | 52 | 64 | 47,998,470 | 11,285,906 |
| 4 | 54 | 56 | 60,869,250 | 13,545,835 |
| 4 | 56 | 32 | 51,144,795 | 8,943,354 |
| 4 | 58 | 32 | 66,594,411 | 10,980,373 |
| 4 | 60 | 16 | 43,070,742 | 7,673,347 |
| 4 | 62 | 0 | 0 | 0 |
| 4 | 64 | 0 | 0 | 0 |

These files cover 347,904,236 integer arc assignments in 74,845,172 tree nodes. Generated and independently checked case/assignment/node counts agree exactly (`logs/exclusion_summary.json`, `exclusion_check.json`). The smaller exclusions at 16 and 28,30,32, together with the general cycle-space bound, establish every lower bound in the table. For a connected graph with N+k edges the cycle-space dimension is k+1, hence the number of distinct simple cycles is at most 2^(k+1)-1. In particular this supplies the other small-order lower bounds and excludes three chords for all N>=34.

**Positive certificates.** `check_witnesses.py` is stdlib-only and does not import any search or symbolic pattern code. It builds the original N-vertex graph, checks simplicity and bipartiteness, and traverses every simple cycle from its least vertex, retaining one orientation. It verifies that the resulting length set is exactly {4,6,...,N}. All 31 rows have passed. As a compact description of the five-chord witnesses, for every even 48<=N<=64 use

```
[(0,5), (0,N-3), (1,N-8), (5,N-40), (N-20,N-1)].
```

This replaces Hamilton edge (5,6) of the 46-vertex witness by a path with N-46 new vertices, and retains the old edge as the fifth chord. The original cycles remain. Edge (5,6) lies on cycles of every even length 30,...,46; stretching those supplies the additional required lengths through 64. Independently checking each full graph, rather than relying on this explanation, certifies every listed order.

**Run the independent checkers from this folder.** No third-party packages, SAT solvers, network, or search code are needed:

```sh
python3 check_witnesses.py witnesses.json --output witness_check_repeat.json
python3 check_exclusions.py certificates/*.bpc.gz --output exclusion_check_repeat.json
```

Run ordinary Python without `-O`, because assertions implement certificate rejection. The complete exclusion check took 183.30 seconds in this session, with one heavy process at a time. The proof files total 4,205,972 bytes compressed; each is loaded separately by the checker. The largest uncompressed proof is about 13.6 MB. Adversarial tests in `test_certificate_rejection.py` also passed: truncation, trailing data, a missing case, an unsound leaf asserting no Hamilton cycle, and a 46-vertex witness with a missing chord were all rejected (`logs/checker_rejection.json`).

To reproduce the search, which is optional for verification:

```sh
clang++ -O3 -std=c++17 exhaustive.cpp -o exhaustive
python3 run_exclusions.py
python3 make_witnesses.py
python3 check_witnesses.py witnesses.json --output witness_check.json
python3 check_exclusions.py certificates/*.bpc.gz --output exclusion_check.json
python3 test_certificate_rejection.py
python3 write_report.py
```

The C++ generator and Python proof checker share no imported implementation. The checker also requires no exported pattern data. `patterns.py`/`export_patterns.py` are search-side tools only. Earlier CP-SAT logs are exploratory, not certificates; an initial zero-arc relaxation produced invalid candidates that the independent witness checker rejected. The final search uses strictly positive arcs and all endpoint-sharing patterns directly.

**Hashes.** These are the authoritative witnesses, proofs, and independent checkers. `SHA256SUMS` also hashes the report, search sources, logs, checked outputs, and primary-source PDFs.

| Certificate / independent checker | SHA-256 |
|---|---|
| `witnesses.json` | `bf85e26b17018676976facb8191e883deac129b262d8eaee71812fae813dfce6` |
| `check_witnesses.py` | `19fabcf738814963b87ee91464780b042fa02b9fc57bd0a515960e65cfd6a219` |
| `check_exclusions.py` | `2955ac563d9eca4306ca4388e96370e677f5909c54ef0d227a8907423751b50d` |
| `certificates/exclusion_k2_n16.bpc.gz` | `b0fa39e161df293cd0375f810a3085c37e288a1c4131ec460744f3aa3d2e1ab8` |
| `certificates/exclusion_k3_n28.bpc.gz` | `6b977d8f886b067853d99c94f862a661a17c3742451c474dd904fdf733e4f980` |
| `certificates/exclusion_k3_n30.bpc.gz` | `7d851f456831dccf1a6e58bfcf1f0902cc53aacece49ff4aada8014bc5418c2e` |
| `certificates/exclusion_k3_n32.bpc.gz` | `9d1a66f816b97772bbfb5c8ffb36f671b95f9040e130f1f9d90f927ff0c6b51e` |
| `certificates/exclusion_k4_n48.bpc.gz` | `64feef5caaa9441fa7c7e3ab15ce02e4b035fc1cad90acade8620291ff712484` |
| `certificates/exclusion_k4_n50.bpc.gz` | `736b4bf63282117cf6533bcaa2ff2077b8fddf8a4f25918976b382fa2aa97ea2` |
| `certificates/exclusion_k4_n52.bpc.gz` | `da9a81a07b69ae3085bbfc3e85bdf64420a0757fc4fed2203b262cdc90d79947` |
| `certificates/exclusion_k4_n54.bpc.gz` | `04ad884fdbc81c4a6746d97a8ba8d798c0b03eb9d759fdad8878bb8d2ec0cddf` |
| `certificates/exclusion_k4_n56.bpc.gz` | `04c9dc0aad9c80d6e0ed7d6486f9c0aba870c3428c7ae3c6da714735fb42bc78` |
| `certificates/exclusion_k4_n58.bpc.gz` | `790ac1d41678fed11426d055ce2582707cb299cd90c343c3a065e388fc76cadb` |
| `certificates/exclusion_k4_n60.bpc.gz` | `65b2c86f67373cada2e998713a1278926b61a129c1ded616032d52e38130eba3` |
| `certificates/exclusion_k4_n62.bpc.gz` | `29f696ad3f648b885cca0b6ebd9d82e99074a131e344e0ae93473e0834e2a453` |
| `certificates/exclusion_k4_n64.bpc.gz` | `4f44fd0e524754077074f0092906b0d26e66d73d1df40beb1ac22988d9ff06d9` |

**Pilot and resources.** The exhaustive pilot first found a valid 44-vertex witness in about 0.003 seconds of search. The 48-vertex exclusion then covered 35,466,805 assignments in about 0.75 seconds of search; independent proof checking took 24.22 seconds in the pilot. The smaller negative pilots at 16 and 28 took under 0.002 seconds each. These measurements justified running the full finite range. All final negative searches together took 5.09 logged seconds; checking dominates the cost. `df -h ~` showed about 15 GiB available at the start and at the last checked stage. The folder remained far below 1 GB. No installations, paid model calls, VM, publication, or messages to others were used. `progress.md` records milestones; the work finished within the first hour.

**Prior art and source corrections.** W. D. Wallis, *Small Bipancyclic Graphs*, JCMCC 102 (2017), 221–228, [publisher PDF](https://combinatorialpress.com/article/jcmcc/Volume%20102/vol-102-paper%2014.pdf), is saved as `sources/wallis2017.pdf`, SHA-256 `80d87a7406eb3c4abe7ebcee589f4ea383f34d1e3982f1451a77bcdf8ec75628`. Its exact table reaches 44, and its last stated bound at orders at least 46 is >=4, not a claimed exclusion of four chords. Its Theorem 2 incorrectly includes 16 in the two-chord interval; p.224 already rules out that case. Here e(16)=3 is independently certified with witness (0,3),(0,5),(0,7). That witness has 10 simple cycles, also disproving p.224's blanket lower count of 11 cycles with three chords when endpoints may be shared. The upper count 15 remains valid. We use e(N) to avoid the paper's inconsistent reuse of m* for minimum edges and minimum excess.

Khodkar, Peterson, Wahl and Walsh, *Uniquely bipancyclic graphs on more than 30 vertices*, JCMCC 98 (2016), 327–342, [author PDF](https://webhome.auburn.edu/~zww0009/UBPCG.v4.pdf), is saved as `sources/unique2016.pdf`, SHA-256 `34122c6fd7ba126e6f6de839cb7a935f0f672fab5c0bd6cfb5a9d0538e9340d9`. Its exactly-one-cycle-per-length condition differs from the present target; the 46-vertex witness here has 25 cycles, not 22. Its cyclic layouts and arc equations are adjacent prior art. George–Khodkar–Wallis's 2016 book and the 2017 paper on (r)-bipancyclic graphs were also located; neither is a later solution to this target.

The scout's cycle-space lower bound at 46 was correct. Its five-chord upper bound was correct but not sharp (one can simply add another legal chord to our four-chord witness). Its ceiling 64 was a valid weak bound; enumerating all kernels sharpens the cycle-count ceiling to 60, and the certified exclusions make the actual four-chord maximum 46.

**Already-solved search record and limits of the claim.** The initial bounded search located no later direct solution. `sources/search_record.md` records all literal queries, author checks, primary links, OEIS results, OpenAlex requests, saved captures, and access gaps. Exact-title OpenAlex requests were rate-limited and the target's own citing list could not be reliably resolved: its citation count is unavailable, not zero. The 2016 book's 11 OpenAlex citing works were retrieved and inspected by title; none identifies this finite table extension. OEIS returned null for `bipancyclic`. The book chapter and relevant full theses were not obtained. Thus the mathematical results above are certified, while historical novelty is only relative to the located literature.

No exact value of e(N) for N>64 is asserted here. For all even N>=48 the established global lower bound is e(N)>=5. No classification or count of all optimal graphs, and no general monotonicity theorem, is claimed.
