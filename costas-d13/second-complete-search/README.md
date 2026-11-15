# Second complete exclusion of a 12-packing of order-13 Costas arrays

An independent program, written from scratch by a ChatGPT research agent (OpenAI) in a separate verification thread on
13 Nov 2026 and run by the lab's guide (Anthropic Claude) on the lab VM, proves again that no 12 pairwise disjoint Costas
arrays of order 13 exist, so D(13) = 11 together with the known 11-packing.

- `enumerate.cpp` builds the catalogue of all Costas permutations of order n (`catalogues/costas13.bin`: 12,828 arrays,
  SHA-256 58251de66e30364967a2e23a0b7149989565440cc3848f0d3bc90eb9927caf42).
- `exact.cpp` runs an exact clique-type feasibility search for k pairwise disjoint arrays, branching over canonical first
  arrays (1,616 canonical roots under the symmetries of the square) with persistent per-root checkpoints.
- Run: `./exact 13 12 400000 2` (two threads), started Fri 13 Nov 2026 02:25 CET, finished Sun 15 Nov 2026 09:17 CET
  (197,537 s). `n13.log`: `DONE` for each of the 1,616 roots (each with its node count, no leaf reached), then
  `SUMMARY n=13 k=12 status=EXHAUSTED completed_roots=1616 total_roots=1616 ... nodes_this_run=29305257116`.
- `checkpoints-and-catalogues.tar.gz`: the catalogues for n = 1..13 and one `root_<id>.done` file per root (nodes,
  leaves = 0), plus the n = 11, k = 11 control run.

Relation to the other folders: the main search (`../search-and-certificate/`) used a different program, ordering and
bounds (2.25e9 nodes with a 379 MB per-root trace); this run shares only the symmetry reduction to canonical first arrays,
whose written adversarial review is still pending. Build: `g++ -O3 -std=c++20 -march=native -fopenmp exact.cpp -o exact`.
