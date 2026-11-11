**Overall verdict: the mathematical claims are confirmed. Historical priority is not established.**

Independent adversarial verification, 11 November 2026. I verified all 31 positive witnesses and independently exhausted every exceptional negative case needed for the table, including all seven four-chord exclusions at orders 48–60. I found no mathematical counterexample or missing endpoint-sharing case. Two literature qualifications are needed: the 29-cycle bound has substantial prior art, and the full text of the relevant 2016 book chapter was not accessible. There is also a minor incorrect page range in the submitted bibliography.

| Claim | Verdict | Independent basis |
|---|---|---|
| The problem matches Wallis's bipancyclicity definition | **Confirmed** | Even order, simple undirected bipartite graph, cycles of every even length through the order |
| Fixing a Hamilton cycle loses no eligible graph | **Confirmed** | The required cycle of length N is Hamiltonian |
| Three chords allow at most 15 simple cycles | **Confirmed** | Binary cycle-space dimension 4 |
| Four chords allow at most 29 simple cycles | **Confirmed; previously known** | Independent finite kernel census; also the result attributed to Shi in Rautenbach–Stella |
| Enumeration covers shared endpoints and respects symmetry | **Confirmed** | Direct completeness argument, independent Burnside counts, and an additional N = 48 exhaustion with no pattern symmetry |
| Two chords are impossible at N = 16 | **Confirmed** | Independent exhaustion; also an elementary cycle-length sum contradiction |
| Three chords are impossible at N = 28, 30, 32 | **Confirmed** | Independent exhaustive searches at all three orders |
| Four chords are impossible at N = 48, 50, …, 60 | **Confirmed** | Independent exhaustive searches at all seven orders |
| e(46) = 4 | **Confirmed** | Four-chord witness verified; three-chord counting bound excludes a smaller excess |
| 46 is the largest four-chord bipancyclic order | **Confirmed globally** | The seven finite exclusions plus the 29-cycle ceiling for every even N ≥ 62 |
| e(N) = 5 for even 48 ≤ N ≤ 64 | **Confirmed** | Verified five-chord witnesses and the preceding lower bound |
| The full minimum-excess table through 64, including e(16) = 3 | **Confirmed** | Witnesses, exhaustive exceptions, and elementary counting bounds |
| These values are new relative to all previous literature | **Unresolved** | No competing table located; full book chapter and a reliable exhaustive citation trail remain unavailable |

**Definitions and reduction.** Wallis explicitly uses finite, simple, undirected graphs and requires the Hamiltonian length. His notation changes meaning: the introductory m*(N) denotes minimum edges, while Theorem 2 uses it for excess. The report's separate e(N) avoids this ambiguity. I checked the local paper and the page images, including the actual inequalities in Theorem 2. [Wallis, *Small Bipancyclic Graphs*, pp. 221–222, 227](https://combinatorialpress.com/article/jcmcc/Volume%20102/vol-102-paper%2014.pdf).

For any eligible N-vertex graph G, choose one required N-cycle H. Every edge outside H joins two vertices of H, so G is exactly H plus |E(G)|−N distinct chords. This holds for every eligible graph, including every graph attaining the minimum. It assumes neither a unique Hamilton cycle nor a special drawing of the chords. Alternating parity along H fixes the bipartition up to interchange. The balanced definition in the book agrees. [George–Khodkar–Wallis, Chapter 6](https://link.springer.com/chapter/10.1007/978-3-319-31951-3_6).

**Counting bounds.** A graph H plus k chords is connected and has binary cycle-space dimension (N+k)−N+1 = k+1. Each undirected simple cycle gives a different nonzero edge vector, so there are at most 2^(k+1)−1 simple cycles. Bipancyclicity needs N/2−1 different cycles, since the required lengths are different. Thus zero chords cannot work beyond 4; one cannot work from 10 onward; two cannot work from 18 onward; and three cannot work from 34 onward. In particular, three chords cannot work at 46, which requires 22 lengths.

For four chords the dimension argument alone gives **31**, not 29. The stronger 29 bound needs additional structure. I independently enumerated all endpoint kernels and counted every nonempty connected 2-regular edge subset. Hamilton arcs and chords have distinct edge identities, so parallel edges in a suppressed kernel are handled correctly.

| Distinct chord endpoints m | Labeled four-chord patterns using all m endpoints | Rotation orbits | Dihedral orbits | Maximum simple cycles |
|---:|---:|---:|---:|---:|
| 4 | 15 | 5 | 4 | 20 |
| 5 | 135 | 27 | 17 | 22 |
| 6 | 330 | 59 | 38 | 24 |
| 7 | 315 | 45 | 27 | 26 |
| 8 | 105 | 18 | 17 | 29 |
| Total | 900 | 154 | 103 | 29 |

Four distinct unordered chords cannot occupy fewer than four endpoints. Every simple cycle of the original graph traverses either a whole suppressed arc or none of it, giving a bijection with kernel cycles; positive subdivisions preserve their number. Consequently the census proves the bound for every order, not just N ≤ 64. At N = 62, 30 lengths are required, already too many. My analogous maximum counts for two and three chords are 7 and 15.

This sharper bound should be credited to prior work. Rautenbach and Stella's introduction states that Shi obtained M(k) = 2^k+k(k−1)+1 for 1 ≤ k ≤ 4, where M(k) maximizes the cycle count over Hamiltonian graphs with k extra edges. Substitution gives M(4) = 29. This is primary literature reporting Shi's result; I did not obtain Shi's full proof. [Rautenbach–Stella, *On the maximum number of cycles in a Hamiltonian graph*, Discrete Mathematics 304 (2005), 101–107, introduction, equation (1)](https://doi.org/10.1016/j.disc.2005.09.007); [Shi (1994)](https://doi.org/10.1016/0012-365X(94)90031-0).

**Completeness and symmetry audit.** List the m occupied chord endpoints in their cyclic order and let a_i be the positive number of Hamilton edges between successive endpoints. Every k-chord graph appears by choosing k distinct unordered endpoint pairs using every endpoint, with m ≤ 2k, then choosing positive a_i summing to N. Shared endpoints are represented directly; contracting zero arcs is unnecessary.

A rotation or reflection of the endpoint circle permutes both chords and arc variables. It preserves positive arc assignments, bipartiteness, edge simplicity, and cycle lengths. Selecting a least image therefore preserves at least one representative of every feasible graph. There is no assumption that arc lengths themselves are symmetric. My separate Burnside calculation reproduces exactly the report's 103 four-chord, 14 three-chord, and 3 two-chord dihedral patterns. The fixed-point counts are saved in `independent_symmetry.json`.

For each endpoint pattern, enumerate all endpoint colors with endpoint 0 fixed to color 0, retaining only opposite-colored chord endpoints. Each Hamilton arc must then have odd or even length according to its endpoint colors. Its minimum is respectively 1 or 2, raised to 3 if the arc would otherwise duplicate an adjacent chord. In the two-endpoint case both arcs receive this restriction. Thus all legal lengths are exactly a_i = b_i+2x_i, with x_i ≥ 0 and sum x_i = (N−sum b_i)/2. No chord can be a Hamilton edge, and no parallel original edges are introduced.

I also read the submitted pattern generation, C++ search, and Python certificate checker. Their connected 2-regular cycle selection and interval exclusion rule are sound: an unassigned 0/1 subset sum is 0, the entire remaining sum R, or lies within [0,R]. If a target length misses every such interval, no completion can supply it. The checker accounts for every branch value and case. I did **not** execute those programs or parse their certificate trees; my numerical verdict rests on fresh exhaustive searches.

**Independent exclusions.** `independent_exhaustive.cpp` generates endpoint patterns internally and selects cycles by testing all kernel edge subsets, rather than importing the submitted symbolic cycle list. Its complete searches retain reflections and quotient only rotations. Every admissible integer composition reaches a leaf and is evaluated exactly; there is no interval pruning. The only whole-pattern pruning is the necessary total-cycle-count bound.

| Chords k | N | Admissible pattern/color cases | Integer compositions actually evaluated | Solutions |
|---:|---:|---:|---:|---:|
| 2 | 16 | 2 | 112 | 0 |
| 3 | 28 | 10 | 22,386 | 0 |
| 3 | 30 | 8 | 29,939 | 0 |
| 3 | 32 | 4 | 21,672 | 0 |
| 4 | 48 | 134 | 38,698,880 | 0 |
| 4 | 50 | 104 | 45,967,570 | 0 |
| 4 | 52 | 68 | 49,131,680 | 0 |
| 4 | 54 | 60 | 62,313,030 | 0 |
| 4 | 56 | 32 | 51,144,795 | 0 |
| 4 | 58 | 32 | 66,594,411 | 0 |
| 4 | 60 | 16 | 43,070,742 | 0 |

The larger counts than the report at 48–54 are expected because I retain mirror images. These complete searches evaluated 356,995,217 compositions. The additional 62 and 64 runs reject all patterns by cycle count before any arc assignment.

To attack symmetry directly, I repeated N = 48 with **no pattern quotient at all**: all 900 labeled endpoint patterns, 804 admissible cases after the necessary cycle-count and coloring filters, and **215,830,758** exact composition evaluations. There were zero solutions. This independently fulfills the requested full exclusion without relying on the submitted symmetry implementation or its proof certificates. See `independent_k4_n48_no_symmetry.jsonl`.

At 16 there is also a short proof. Shared-endpoint or noncrossing two-chord patterns have only six cycles, fewer than the seven needed. The crossing pattern has seven; their lengths sum to 16+18+18+20 = 72, whereas the seven required lengths sum to 70. Seven cycles covering seven required lengths would have to have exactly those lengths, a contradiction.

**Independent positive checks.** `independent_witnesses.py` reads only the submitted witness data. It constructs each original N-vertex graph, rejects repeated edges or same-color chords, and enumerates all vertex-simple cycles. Taking the least cycle vertex as root and retaining one orientation counts each undirected cycle once. It also checks uniqueness of the resulting edge sets. All 31 witnesses pass. The input witness SHA-256 is `bf85e26b17018676976facb8191e883deac129b262d8eaee71812fae813dfce6`.

For the specific 46-vertex witness `[(0,5), (0,43), (1,38), (26,45)]`, I find **25** simple cycles. Every even length 4–46 occurs once except length 20, which occurs three times, and length 34, which occurs twice. The graph is bipartite and has exactly 50 edges. Hence e(46) ≤ 4; the three-chord counting bound supplies the opposite inequality.

Every listed five-chord witness at 48–64 has 39 simple cycles and contains every required length. At 16, `[(0,3), (0,5), (0,7)]` has ten simple cycles and every even length 4–16. All cycle vertex sequences and histograms are saved in `independent_witnesses.json`.

As a cross-check on my kernel code, its complete cycle-length histograms agree with original-graph DFS on 121 graphs: all 21 submitted witnesses having one to four chords, and 100 reproducible random bipartite Hamilton-cycle-plus-chord graphs. The exhaustive program also independently finds positive examples at 14, 26, and 46; expanding and checking each with original-graph DFS succeeds. The comparison script is `independent_crosscheck.py`; results are in `independent_crosschecks.json`.

**Resulting exact table.** The upper bounds above and the counting bounds plus exceptional exclusions give precisely:

| Even N | e(N) |
|---|---:|
| 4 | 0 |
| 6–8 | 1 |
| 10–14 | 2 |
| 16–26 | 3 |
| 28–46 | 4 |
| 48–64 | 5 |

Together, the finite exclusions at 48–60 and the global 29-cycle bound establish e(N) ≥ 5 for **every even N ≥ 48**. Thus 46 is the global four-chord maximum. No monotonicity assertion is used. This settles the stated finite table and the four-chord threshold, not the general minimum-excess function beyond 64.

**Source corrections and priority.** Wallis's printed Theorem 2 includes 16 in the two-chord interval, although p. 224 already excludes it. Its final inequality is ≥4 for N≥46, not >4. The report corrects these readings properly. The same page's lower count of eleven cycles with three chords fails for the ten-cycle shared-endpoint witness above. [Wallis, pp. 224, 227](https://combinatorialpress.com/article/jcmcc/Volume%20102/vol-102-paper%2014.pdf).

The 2016 book is directly relevant: Chapter 8, *Minimal Bipancyclicity*, pp. 99–106, addresses the minimum-edge function. I verified its publisher record and abstract. The PDF request returned subscription-preview HTML; Google Books page requests returned unavailable-image placeholders, and subsequent searches were rate-limited. I therefore cannot certify that the book does not contain an earlier equivalent table or construction. Merely predating Wallis's paper would not rule that out. [George–Khodkar–Wallis, Chapter 8](https://link.springer.com/chapter/10.1007/978-3-319-31951-3_8). Access responses are recorded in `literature_access.jsonl`.

The located adjacent results do not settle this minimum-excess problem. Khodkar–Peterson–Wahl–Walsh require exactly one cycle of each length. Khodkar–Sawin–Mueller–Choi require a fixed exact multiplicity for every length; their enumeration is not a classification of arbitrary bipancyclic graphs. [UBPC paper, author version](https://webhome.auburn.edu/~zww0009/UBPCG.v4.pdf); [(r)-bipancyclic paper, §§1, 4](https://www.wonhyuk.com/publications/pdf/jcmcc17.pdf).

One bibliographic correction: the UBPC paper is in JCMCC 98 (2016), **351–374**, rather than 327–342 as stated in `result.md`; the latter pages belong to another article. [Publisher article record](https://combinatorialpress.com/jcmcc-articles/volume-098/uniquely-bipancyclic-graphs-on-more-than-30-vertices/).

Targeted searches for the exact Wallis title, minimum bipancyclic excess, four/five chords, orders 46 and 48, later work, and book errata found no competing resolution of the asserted finite table. These negative search results do not establish novelty. In particular, the known 29-cycle result must not be presented as a new discovery, and the missing book chapter remains a material priority gap.

**Reproduction and resources.** All new programs and outputs are in this folder. No submitted program was executed or imported. No installations, paid calls, VM, publication, or messages to others were used. All numerical searches were single-threaded and run serially. The recorded exhaustive-search CPU time is about 21.3 seconds including the extra no-symmetry run, comfortably within the 30 CPU-minute limit.

```sh
python3 independent_witnesses.py
python3 independent_symmetry.py
clang++ -O3 -std=c++17 independent_exhaustive.cpp -o independent_exhaustive
./independent_exhaustive census 4
./independent_exhaustive 2 16
./independent_exhaustive 3 28
./independent_exhaustive 3 30
./independent_exhaustive 3 32
./independent_exhaustive 4 48 all
./independent_exhaustive 4 50
./independent_exhaustive 4 52
./independent_exhaustive 4 54
./independent_exhaustive 4 56
./independent_exhaustive 4 58
./independent_exhaustive 4 60
```

Full numerical logs are `independent_runs.jsonl`, `independent_k4_n48.jsonl`, and `independent_k4_n48_no_symmetry.jsonl`. These are fresh computations, not replays of the submitted certificates.
