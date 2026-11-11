# athanor-combinatorics

**Archived release v1.0:** Zenodo [10.5281/zenodo.24140011](https://doi.org/10.5281/zenodo.24140011) (all versions: [10.5281/zenodo.24140010](https://doi.org/10.5281/zenodo.24140010)). The record also holds the full 379 MB Costas search trace `no_12_order13.proof.gz`.

Certified computations on long-stalled combinatorial questions (November 2026).

| Folder | Question (source) | Result | Status |
|---|---|---|---|
| [`costas-d13/`](costas-d13/) | Maximum number D(13) of pairwise disjoint Costas arrays of order 13: is it 11 or 12? (Frank–Dinitz, JCMCC 93, 2015) | **D(13) = 11** | Computationally established, as detailed below |
| [`bipancyclic/`](bipancyclic/) | Minimum number of edges of a bipancyclic graph (Wallis, JCMCC 102, 2017): is e(46) 4 or 5? | **e(46) = 4**; exact e(N) for all even N ≤ 64; correction e(16) = 3 | Independently verified |
| [`qcover-104/`](qcover-104/) | q-covering number C₂(6,3,2), previously 99 ≤ C ≤ 105 (Etzion 2014; Cossidente–Pavese 2016) | **C₂(6,3,2) ≤ 104** (explicit 104-block cover) | Peer-reviewed: [rStation math_27](https://rstation.ai/problems/math/papers/27/v1); Zenodo [10.5281/zenodo.24125169](https://doi.org/10.5281/zenodo.24125169) |

### Costas D(13) = 11: what supports it

- **The full search** is in `costas-d13/search-and-certificate/`. An exact clique search over all 12,828 order-13 Costas arrays found no 12-packing: 2,249,110,973 nodes, D4 symmetry roots, colouring bounds. An independent per-root audit of its 379 MB trace passed. The trace is in the Zenodo record above, because it is too large for git. The solver is 3.28× faster than our first version, with the same node counts.
- **A first, separate search** (`costas-d13/first-search-partial/`) excluded the first 157 root families and agrees exactly on the first 40 roots.
- **An independent re-implementation** (`costas-d13/independent-solver-and-catalogue/`) works without symmetry reduction.
  - It re-enumerates all order-13 Costas permutations and finds 12,828, matching the catalogue.
  - It reproduces D(9) = 8, D(10) = 10, D(11) = 10 (a full exclusion) and D(12) = 12.
  - It covered the 35 heaviest order-13 roots without finding a 12-packing. It is not a complete second exclusion.
- **Still pending:** a written adversarial review of the symmetry-reduction argument.

### Bipancyclic graphs

Witness for N = 46: chords (0,5), (0,43), (1,38), (26,45) on C₄₆. Four chords are impossible for every N ≥ 48: exhaustively for 48–60, and by a cycle-count bound for N ≥ 62. An independent audit (`bipancyclic/audit/`) re-ran the N = 48 exclusion without symmetry: 215,830,758 assignments, none valid.

## Provenance and credit

These results come from a programme on long-stalled published questions. AI research agents worked under the direction of the author of record (Aleksei Kudriashov, ORCID 0009-0006-8885-5338), who takes responsibility for the content:
- OpenAI GPT-6.1 "Sol" cores ran the searches, proofs and independent audits;
- Anthropic Claude orchestrated them.

Every result was checked by a separate session that did not run the solver's code. The checks are in each folder: certificates, stdlib checkers and audit reports. Downloaded third-party papers are not redistributed here.

We claim priority only as far as the dated literature searches recorded in each folder go. Corrections are welcome as issues or pull requests, from people and AI agents alike.

## License

Code: MIT. Data, certificates and text: CC BY 4.0. Third-party inputs (e.g. the Costas array catalogue) keep their original terms and are credited where used.
