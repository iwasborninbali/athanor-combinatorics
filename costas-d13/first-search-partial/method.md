# Definitions and complete-search logic

A permutation `a` represents dots `(r,a[r])`, with both coordinates zero based.
Two arrays are adjacent exactly when `a[r] != b[r]` for every row `r`.
No translations, row permutations, column permutations, or identification of
dihedral variants is implicit in this graph. Every distinct catalogue array is
a vertex. Costas validity means the displacement vectors between all unordered
dot pairs, oriented by increasing row coordinate, are distinct.

## Catalogue input

The data are the `Searches/Sorted_Costas_arrays_N=n.txt` members of Beard's
`Costas_folder_Searches.zip`, copied from the scout's saved original. Each file
starts with the order and number of arrays. The subsequent lines are full
zero-based permutations, including all rotations and reflections, rather than
only equivalence-class representatives. Exact archive-member equality and
SHA-256 hashes are recorded in `sources/catalogue_provenance.json`.

Catalogue completeness is an external input, not something implied by validity
and distinctness tests. Frank–Dinitz, manuscript p. 2, explicitly uses the
complete listing through order 27, and Table 3.1 has 12,828 arrays at order 13.
Beard's Files page supplies the searched database separately from the much
larger algebraically generated database. His 2007 preprint, section IV, discusses
exhaustive search and cites the earlier comprehensive searches through order 17
by Silverman, Vickers and Mooney (1988), DOI 10.1109/5.7156. OEIS A008404
corroborates the full-array convention and count. The historical search was not
independently reproduced here; statements extending exclusion to all Costas
arrays are conditional on this published completeness input.

## Clique search and symmetry coverage

Let `rep(v)` be the least catalogue index among the eight rotations/reflections
of vertex `v`. The catalogue is checked to be closed under these operations.
The C++ search makes one root for each `i` with `rep(i)=i`, selects `i`, and
allows precisely its neighbors `j` with `j>i` and `rep(j)>=i`.

This covers every clique up to a single common symmetry of the whole board.
For a clique C, take the least index q in the union of g(C) over all eight
symmetries g. Choose one symmetry that brings a member of C to q. In that
transformed clique, q is a representative; all other members have index greater
than q and representative at least q. Thus the clique occurs in root q.
This argument does not apply a different symmetry to each chosen array.

At a node the selected vertices form a clique, P is the common candidate set,
and `need` is the number still required. A proper coloring partitions P into
independent sets C1,...,Ct. Each cell group of any fixed row or column is an
independent set; an additional greedy partition is also used. Colors are ordered,
then vertices within each color by increasing catalogue index.

The search considers vertices in the reverse of this order. For each eligible
v it recurses on the intersection of its neighbors with the unprocessed prefix,
then removes v. Every possible completion has a unique greatest vertex in this
order. If that vertex has color j, then j must be at least `need`, since its
prefix has only j colors and a clique uses each color at most once. This
justifies stopping when the remaining prefix has fewer than `need` colors.
The other leaf rule, fewer than `need` candidates, is immediate. No claimed
exclusion can use a timeout or an incomplete root.

## Compact trace and independent checking

The gzip trace has one byte for each visited node:

- 0 to n-1: use the cell partition of that row;
- n to 2n-1: use the cell partition of that column;
- 254: use the deterministic greedy independent-set partition;
- 253: a leaf closed by candidate cardinality.

Cell groups are ordered by decreasing size, breaking ties by their least vertex;
vertices in each group are ascending. Greedy groups repeatedly take the least
available vertex and remove its neighbors from that group. After all roots of a
completed negative search, the stream ends with `ENDPROOF`. A positive search,
timeout, disk stop, truncated stream, or missing root cannot pass the checker.

`check_clique_proof.py` is separately written in stdlib Python. It validates every
catalogue permutation and Costas property, rebuilds the graph via per-cell bit
sets, reconstructs the symmetry action, verifies proper colorings, and checks
every required child and completion marker. It imports neither search code nor
a SAT solver and does not execute the search binary. The bytes only guide which
coloring to verify; they cannot authorize a branch omission. Its reconstruction
of row and column partitions uses integer bit sets rather than the C++ vectors
and fixed-width bit blocks.

`check.py` independently checks positive certificates by direct enumeration of
all dot pairs and occupied cells. Positive validity does not require catalogue
completeness; optional catalogue membership checks validate the recorded indices.

## SAT and heuristic trials

`search_cpsat.py` selects exactly k arrays, with an at-most-one constraint through
each cell. Its optional `--holes` formulation for k=n-1 adds one Boolean hole
per cell, requires exactly one selected array or hole in each cell, and exactly
one hole in each row and column. Both formulations are equivalent: k disjoint
permutation arrays occupy k cells per row and column. Solver UNKNOWN and local
search timeouts have no exclusion meaning. No CP-SAT infeasibility is used as a
standalone mathematical certificate.

`make_holes_cnf.py` gives a library-free SAT encoding of the same hole model.
For a list x1,...,xt it emits the cover clause and a sequential AMO chain with
fresh s1,...,s(t-1): x1 implies s1; each interior xi implies si and not s(i-1);
s(i-1) implies si; xt implies not s(t-1). Two true xi would force a contradiction
along the chain. For zero or one true xi a satisfying chain extension exists;
the cover clause excludes zero. Thus each group is exactly one. The full-packing
pilot variant forces all hole variables false instead of imposing one hole per
row and column.

The optional SAT symmetry restriction introduces prefix OR variables pi for
the selected array variables x0,...,xi and requires xv to imply p(rep(v)).
Thus the least selected index is a representative and no selected vertex has
an orbit representative below that index. The common-board-symmetry argument
above proves this restriction preserves existence. It is existential symmetry
breaking, not a constraint that every packing already satisfies.

`check_sat_encoding.py` independently validates the catalogue and reconstructs
every expected clause and all variable allocations without importing the CNF
generator. Its separate symmetry computation uses repeated rotations and a
reflection. With `--proof` it streams a gzip binary DRAT proof to the separately
installed `drat-trim` and requires `s VERIFIED` and a successful exit. Encoding
verification alone is not an UNSAT result. A SAT assignment is converted by
`extract_sat.py` and then checked using `check.py`.

Two alternate AMO representations are available. The binary auxiliary encoding
assigns a distinct bit code to each choice; selecting a literal forces that code.
Distinct choices therefore cannot both be selected, and a single choice has a
consistent auxiliary extension. The cover clause again forces exactly one.
The direct-conflict encoding emits one binary clause for each overlapping pair
of catalogue arrays, plus array-versus-hole conflicts, cell cover clauses, and
exactly-one-hole constraints in each row/column. These clauses express the same
packing existence problem. `check_pairwise_cnf.py` independently reconstructs
every direct conflict using per-cell integer bitsets and can stream the expanded
gzip CNF through a workspace-local FIFO to `drat-trim`.

Time-sliced clique runs are discovery trials. Their summaries count cut roots
and report INCOMPLETE or TIMEOUT whenever any required root is unfinished.
They never produce a completed exclusion marker. Reordering by graph degree
only permutes the same input arrays; an accompanying index map preserves the
original catalogue row numbers. Positive witnesses are checked from their dots,
regardless of ordering. General negative conclusions require all cases and an
independently checked complete certificate.

An additional necessary matching test was piloted. At a partial selection,
any currently vacant cell not occupied by any remaining candidate must be a
hole in a completed (n-1)-packing. More than one such cell per row or column
already violates a cell-partition bound. Otherwise those forced holes must
extend to a perfect matching of the currently vacant board cells. A failed
augmenting-path test provides a Hall-deficient set of rows. Opcode 252 records
its row mask as four little-endian bytes. The independent Python checker derives
the allowed hole positions anew and checks that their union has fewer columns
than the number of specified rows. It need not reproduce the matching search.
`check_hall_cut.py` audits a standalone recorded state; its conclusion applies
only to that state's selected arrays and listed candidates. This test cut very
few nodes in the initial order-13 pilot. The build flag
`-DDISABLE_HOLE_MATCHING` omits it for comparison.

An optional recolouring pilot uses opcode 251: start with the canonical greedy
classes, then read a byte count and that many pairs (local candidate index,
destination original class). Every move is checked to keep its destination
independent; empty classes are removed afterwards. It is limited to at most 64
candidates. Both independent checkers accepted the complete order-11 pilot.
It reduced nodes from 1,678,389 to 1,488,919 but increased search time from
13.70s to 15.60s, so it was not enabled in the target continuation.

A trace-guided continuation can resume an interrupted ordinary clique trace:
`clique_resume CATALOGUE TARGET SECONDS NEW_PREFIX resume OLD_PREFIX.proof.gz`.
It copies the original gzip trace to a different output prefix, reconstructs the
already-recorded tree from its color advice, and begins writing a new gzip member
at the first unrecorded node. Completed ancestors continue with their remaining
branches. Gzip concatenation preserves the single logical certificate stream.
Continuation currently accepts traces without Hall opcodes; the long target run
uses the build without that bound. A truncated order-9 pilot was resumed and its
decompressed full trace matched the uninterrupted trace exactly; the independent
Python checker also accepted it. A resumed negative still requires the complete
independent check. Search-time greedy lower witnesses are checked from their dots.

The final target build also tests the canonical greedy coloring first on small
candidate sets. If it already uses fewer than `need` colors, that node closes
immediately; no row/column scores need to be computed. Otherwise the original
partition-selection rule is used. The full order-11 pilot visits the same
1,678,389 nodes and its new trace passed independent checking. This changes
only color advice at already closed nodes, and adds no new pruning principle.
Small nodes use sorted candidate vectors to avoid scanning mostly empty global
bit blocks; this representation change alone reproduced full pilot traces
byte-for-byte. All graph edges are still defined by the actual occupied cells.

For partial reporting only, `check_clique_prefix.py CATALOGUE TRACE TARGET K`
and `check_root_prefix CATALOGUE TRACE TARGET K` audit exactly the first K
canonical roots. Their output explicitly says that restricted scope and records
the last catalogue index checked. They deliberately do not require global
completion or inspect later data. They are not substitutes for the full checker
and do not establish a global bound unless every root is separately covered.
They agree on a five-root order-9 pilot.

## Parallel independent audit (one process)

The optional index has lines `end_root_ordinal end_uncompressed_byte_offset`.
Root ordinals are zero based; ends are exclusive. Consecutive lines partition
all canonical roots and the proof bytes. The index comes from search progress
counts, but it has no evidential authority. `check_trace_parallel.cpp` rebuilds
the root list independently and requires that the ranges cover every root,
without gaps. Each worker reconstructs its assigned roots from the catalogue,
checks every recursive obligation, and requires its byte interval to be consumed
exactly. A false offset, skipped root, or falsely closed branch is rejected.
The whole gzip stream, all CRCs, ENDPROOF and EOF are also checked. Three threads
run inside one heavy process; the graph is small and the gzip files are streamed,
not expanded to disk or held entirely in memory. No search code is linked.

The full order-11 trace passed this verifier in 1.82357 seconds, versus 4.14710
seconds serial. Invalid offsets, missing root ranges, changed root ordinals,
invalid opcodes, missing completion and truncated gzip footers were rejected.
The serial C++ and stdlib Python full verifiers need no index and check the same
original certificate. The target audit records the index SHA-256 as well.

`check_prefix_parallel.cpp` is a deliberately separate scoped variant. It checks
only the stated initial K roots, and validates all assigned bytes and the gzip
integrity; it makes no claim about later proof data. It agrees with the stdlib
Python checker on a five-root order-9 case and the serial checker on a forty-root
order-11 case. Intermediate ranges use fully recorded 20-root milestones. The final scoped
range checks an explicit count of completed roots and may leave later, unclaimed
bytes unread; its final offset is only an upper bound. The verifier reports the
actual consumed position. This is the same restricted-root logic as the serial
and Python prefix checkers, and does not authorize any omitted child inside a
claimed root.

If the programme reaches a resource stop before all roots finish, a checked
prefix permits an exact reduced continuation without replay. Let Q be the last
checked representative index. Any 12-clique containing an array with
representative at most Q would, under one common D4 transformation, belong to
one of the excluded roots. Every hypothetical 12-clique must therefore use only
arrays whose representative is greater than Q. Removing exactly those first
orbits yields a D4-closed induced subgraph. A complete exclusion of 12 there,
together with the prefix exclusion, covers all original cases. The stdlib-only
`check_chained13.py` independently verifies this precise data relation and can
traverse both component proofs using the separate Python decoders. A filtered
catalogue is not asserted to contain all order-13 Costas arrays; the checked
reduction is essential to the combined argument. Preparing this checker alone
establishes no exclusion or bound.

The bounded reduced continuation can use `clique_threaded.cpp`, which runs up
to three independent root searches in one process. The graph is shared read-only;
paths, counters, gzip outputs and cancellation state per root are separate.
Only when every root finishes negative are the root gzip members concatenated
in canonical order and ENDPROOF appended. The independent checker then verifies
the complete result; the search's done flags are not proof. Complete order-9 and
order-11 traces were byte-for-byte identical after decompression to the serial
search and passed independent checking; an order-12 witness passed the stdlib
checker. The parallel search is not used to bypass the six-hour deadline.


## Scope actually certified in this programme

The first audit checked the first 109 original roots, through representative
index 130. The second checked the first 48 roots of the exact remaining graph.
Deleting complete D4 orbits preserves the order of the remaining canonical
representatives. Applying the preceding reduction argument twice therefore
excludes the first 157 original root families, through representative index
195, and leaves exactly 11,580 vertices in 1,459 D4 orbits. These two restrictions
are the only asserted order-13 exclusion. They are not a proof against all
12-packings. The independent stdlib filter checker recomputed the combined
remaining set directly from the original permutations.

The two C++ audits checked 1,766,537,963 and 298,797,712 nodes, respectively.
The second used `check_prefix_parallel_stack.cpp`, with explicit 8 MiB thread
stacks and the same scoped proof logic. Audit JSON records bind the actual
source, executable, catalogue, boundary index and proof hashes. Full Python
traversals of these large prefixes were not run; the stdlib implementations
were validated against complete smaller cases and restricted-root pilots.
