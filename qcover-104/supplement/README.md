# Supplement: a 104-block binary subspace cover

This package verifies the explicit upper bound C₂(6,3,2) ≤ 104 and the full
ambient projective semilinear stabilizer C₂ × C₂ of the supplied witness.
It does not prove optimality. The known lower bound is 99.

## Run from a clean unzip

Python 3.10 or later, standard library only. No installations, network access,
solver, compiler, or original research directory are required. Run ordinary
Python, without `-O`, since the checkers use assertions.

```sh
python3 checker.py --hashes
python3 check_rank.py certificates/cover104.json --max 104
```

The first command resolves its data paths relative to the script, so it also
works when invoked by absolute path from another directory. Both commands
print freshly computed JSON and exit nonzero on a failed check. They do not
write files. Coverage and stabilizer replay are typically light computations;
the separate rank checker performs 1,953 × 104 small Gaussian-rank tests.

## Certificates and checks

- `certificates/cover104.json` is the original, byte-preserved main certificate.
  Integers encode coordinates in bits 0 through 5, least significant first.
  Each entry of `basis_rows` is three independent nonzero vectors and denotes
  their binary row span. `cover104.txt` is the same list of triples.
- `certificates/pavese_105.json` is the reconstructed 105-block starting cover,
  attributed to Cossidente–Pavese (2016), as restated by Pavese (2020),
  Construction 4 and Theorem 5. This is prior art.
- `certificates/trade_105_to_104.json` records the 95 removed and 94 added
  blocks. The covers share ten blocks. The checker verifies the complete set
  difference using subspaces, so changing a basis would not change the test.
- `checker.py` adapts the independently written audit's XOR-closure,
  orthogonality, invariant refinement and exhaustive stabilizer algorithms
  into a single self-contained entry point. It does not import search code,
  precomputed incidence data, or historical audit reports. In particular it
  recomputes the invariant classes and tests all 4,096 surviving full image
  bases against the block family. The printed generators and exhaustive
  survivor set establish the full group, not merely a subgroup. It also
  verifies dual coverage and the absence of a stabilizing correlation.
- `check_rank.py` is the byte-preserved, separately written internal
  Gaussian-elimination checker. It checks ranks, block uniqueness and coverage
  of all unordered pairs of distinct nonzero ambient vectors. It accepts an
  explicit certificate path and a maximum block count.
- `SHA256SUMS` covers all distributed files except itself. Hashes identify
  bytes; the mathematical checkers independently verify the finite claims.

The main certificate's SHA-256 is
`af7612a2a0a05e64265a7d44ca35039d033e72e40102a1bec2d122ace887727b`.

## Historical records and priority

`independent-audit.md` explains the independent audit and its scope.
`audit/independent_check.json` and `audit/automorphisms.json` are the original
audit outputs, retained for comparison. Their numbers are not inputs to the
fresh computation. `audit/target_local.log` is the original discovery log;
no search algorithm is needed for verification, and this package does not
reproduce the heuristic's trajectory or timing.

`audit/verify-original.txt` and `audit/search_record.txt` preserve the original
11 November 2026 reports verbatim. Their commands and relative links refer
to the original research directories, not to this package. They are archived
as plain text to distinguish those historical references from bundle links.
The original retrieval archive is not redistributed. `audit/source_manifest.json`
records the reports' hashes and selected primary-source URLs and hashes;
`audit/original_retrieval_sha256.json` identifies the larger original archive.
The hashes cannot substitute for access to those sources or for an exhaustive
literature search. Priority is provisional: no published or arXiv-posted
bound ≤104 was found in the recorded search; Bayreuth live-table access failed.

## Provenance

OpenAI GPT-6.1 “Sol” research cores performed the search, analysis, writing
and independent audit, with Anthropic Claude as orchestrator, working with
Aleksei Kudriashov as responsible author of record. Two internal checkers,
the Guide's own script and the independent verifier confirmed the witness,
as recorded in the research handoff. The Guide's separate script is not part
of this package. The independent verifier's algorithms and the separate
internal rank checker are supplied here. Aleksei Kudriashov takes responsibility
for the paper's content.
