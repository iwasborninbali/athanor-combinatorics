# Correctness of the speed solver

This is an exact clique decision solver over the same full catalogue as the baseline. The catalogue's completeness is an external input; validating every listed array does not establish completeness. `data/catalogue_provenance.json` is copied from the peer workspace and records the archive provenance. All array and root indices in this workspace are zero based. A **root ordinal** is its position in the increasing list of canonical catalogue indices, not a catalogue index.

## Graph and local representation

For permutations a and b, adjacency means a[r] != b[r] for every r. The large-node engine retains the baseline's pairwise graph construction. When a candidate set U has at most 512 members, the new kernel assigns them local indices in increasing catalogue order. For each board cell (r,c) it builds the bitset I[r,c] of members of U using that cell. Its neighbourhood for local vertex v is

    U minus union over r of I[r, a_v[r]].

A vertex is in that union exactly when it shares a cell with v, so this is precisely the induced disjointness graph, including a zero diagonal. No edge approximation occurs. At every descendant, `P & edge[v]` is the intersection of the still-active candidates with v's neighbours. A local kernel's universe remains fixed throughout its subtree; masked-out members never return. The global and local bitsets therefore represent exactly the same candidate sets.

## Symmetry roots

Let rep(v) be the least catalogue index among the eight board rotations/reflections of v. Every image must be present in the catalogue; missing images are an error. For a clique C, take q to be the least index in the union of g(C) over all eight common board symmetries g. Choose a single g taking one member of C to q. Then q is canonical, every other member of g(C) has index greater than q, and its representative is at least q. Thus some solution occurs among the roots q=rep(q), with candidates j>q and rep(j)>=q. We do not transform different arrays independently. These are precisely the baseline's roots.

## Colour bounds and complete branching

At a node the selected vertices are a clique and P is the active set of their common neighbours. Let `need` be the remaining target size. A fixed row's occupied-cell classes are independent sets: two arrays in one class share a dot. A column's classes have the same property. A greedy class is constructed by repeatedly choosing the least remaining vertex and deleting its neighbours from the class's available set. It is therefore also independent. Both constructions partition P.

Number the classes 1 through t and concatenate them in that order. Vertices within a class are in increasing catalogue order. Branch in reverse order, removing a vertex after visiting its child. A possible completion has a unique greatest vertex in this order; its other members are in that vertex's still-active prefix and its neighbourhood. Every completion is therefore visited. A prefix ending in class j has a proper j-colouring and cannot contain a clique larger than j. Returning when j<need is sound. Cardinality pruning, |P|<need, is immediate. Reaching `need==1` with an eligible vertex produces an actual witness, not an exclusion.

Classes for a cell partition are ordered by decreasing size, with ties broken by their least member. The baseline chooses the partition whose classes numbered at least `need` contain the fewest vertices, comparing this score with the canonical greedy partition. The optimized score calculation is exactly the same sum. If there are `need` nonempty classes it is the smallest size; if there are `need+1` it is the sum of the two smallest sizes. Other cases retain a full sort. The shortcut affects only how a number is calculated, not its value or admissibility. In the requested full-pack and one-hole problems there cannot be more than `need+1` classes, because every candidate avoids every previously selected cell.

Testing the greedy colouring before scoring rows/columns may close a node using a different valid colour advice byte. Both tests prove that the node has no completion. On nodes that remain open, the score, tie rules and branch order are unchanged. Consequently the explored state tree is the same as the baseline's; decompressed advice streams need not be identical. Equality of node counts is an observation in the benchmarks, while exactness follows from the partition argument above.

There are no Hall, matching, recolouring, incumbent, timeout-as-exclusion, floating-point, or probabilistic pruning rules in the production build. A time limit, root slice, I/O failure or missing root cannot support a global negative answer.

## Parallel coverage and traces

Roots are independent decision subproblems. One production process takes even canonical root ordinals and the other odd ordinals. They share no search state and cannot omit each other's work. Each completed root has its own gzip member containing exactly the baseline trace opcodes:

- 0..n-1: the indicated row partition;
- n..2n-1: the indicated column partition;
- 253: a cardinality leaf;
- 254: the canonical greedy partition.

No per-root completion marker is put inside these members. A merger requires every expected ordinal exactly once, a completed status in both summaries, and matching catalogue root indices. It concatenates the members in canonical root order and appends a gzip member containing `ENDPROOF`. Concatenated gzip members decode as one stream. This is the existing full-checker format. A missing, extra, truncated, corrupt or false tree cannot pass full independent verification merely because a summary claims exhaustion.

The unchanged copied `checkers/check_trace.cpp` reconstructs the catalogue, its validity, the graph via global cell incidence, all canonical roots and every child required by the advice; it requires the completion marker and EOF. The unchanged copied `checkers/check_clique_proof.py` is an additional stdlib checker. `checkers/audit_speed.py` was written here independently and reconstructs the proof using Python integer sets; it imports neither solver nor peer checker. Positive witnesses are checked with the copied `checkers/check.py`, directly from all displacements and occupied cells.

`checkers/check_roots.cpp` differs from the copied C++ checker only by explicit root selection, reporting that scope, and requiring `ENDROOTS`. It is for sample/shard audits, never for silently treating a subset as a global result. A fixed-root benchmark summary's `EXHAUSTED` refers only to its selected roots; a global claim requires complete root coverage and verification.

The actual full-order-13 audit may use two modulo scopes in parallel to meet the wall-time budget. The only C++ checker changes are the root selector, the explicit scope fields and `ENDROOTS` instead of `ENDPROOF`. It reconstructs the same node trees independently. Even and odd root ordinals form disjoint sets whose union is the entire root list; each scoped audit checks its entire set and EOF. The merger validates the expected root list independently. `stream_scope.py` reads exact compressed member slices from the joined proof, checks every slice's SHA-256 against the merger's record, and emits the scoped marker only after all slices have been read. This binds the two checked forests to the published full certificate. A split-and-check regression on the fully checked order-11 proof validates the selector/streaming wrapper.

The merger additionally validates each root gzip member's CRC, allowed production opcodes and decoded byte length. Because every production opcode is exactly one byte, that length equals the root's recorded node count. The independent scoped checker emits its own per-root node counts and canonical indices, without receiving the manifest. The finisher requires each independently verified root count to equal that member's decoded length. This checks logical root boundaries, as well as the union of the two scopes; it prevents a valid parity forest from concealing a misplaced boundary in the joined global stream. The final gzip member is separately decoded and required to be exactly `ENDPROOF`.

To keep storage bounded, the merger writes a recovery map before assembly, appends each original compressed root member, flushes and fsyncs that exact copy, and only then deletes its redundant standalone file. Thus the original gzip members remain recoverable byte for byte by the lengths in `order13_merge_plan.json`; the assembly does not need two full copies of the proof. The later embedded-member audit checks their hashes and the global completion member before independent tree verification starts.
