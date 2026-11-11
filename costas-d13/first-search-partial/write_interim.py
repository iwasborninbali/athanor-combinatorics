"""Write an explicitly interim report while the target computation is active."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from check import check

stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
certificates = []
for p in sorted(Path('certificates').glob('*')):
    if p.name == 'SHA256.json':
        continue
    certificates.append({'file': str(p), 'bytes': p.stat().st_size,
                         'sha256': sha(p)})
Path('certificates/SHA256.json').write_text(json.dumps(certificates, indent=2)+'\n')
selected = ['witness_9_8.json', 'no_full_9.proof.gz', 'no_full_11.proof.gz',
            'witness_10_10.json', 'witness_12_12.json',
            'witness_14_12.json', 'witness_17_12.json']
table = '\n'.join('| '+r['file']+' | `'+r['sha256']+'` |'
                  for r in certificates if Path(r['file']).name in selected)
audits = []
for n, size in [(9,8), (10,10), (12,12), (14,12), (17,12)]:
    audits.append(check(f'certificates/witness_{n}_{size}.json', f'data/costas_{n}.txt'))
Path('logs/delivered_witness_audits.json').write_text(json.dumps(audits, indent=2)+'\n')
text = f'''# Interim research report — {stamp}

**The target is not yet settled. Computation is in progress.** No 12-packing or independently checked complete exclusion of 12 at order 13 has been obtained. The published interval remains **11 ≤ D(13) ≤ 12**. This file will be revised when the run ends.

## What is currently established

The independent stdlib checker verifies a size-8 order-9 witness and a complete exclusion of size 9, reproducing D(9)=8 conditional on its published catalogue completeness. Complete exclusion of 11 arrays at order 11 was independently checked in both Python and a separately written C++ verifier. Full order-10 and order-12 witnesses, and 12-array witnesses at orders 14 and 17, were checked directly. These reproduce known results and give no new order-13 bound.

All witness permutations use zero-based coordinates: the entry at position r is the dot's column in row r. Disjoint means distinct occupied cells. Each Costas check tests all n(n−1)/2 displacement vectors, oriented by increasing row index.

## Catalogue and completeness input

The input is `Searches/Sorted_Costas_arrays_N=13.txt` from [Beard's searched catalogue archive](https://jameskbeard.com/Files_for_download/Costas_folder_Searches.zip), preserved as `data/costas_13.txt`. It contains **12,828 distinct valid permutations**, including rotations and reflections separately, and **1,616 D4 orbits**. It is not the essential-representative or algebraically generated catalogue. Exact archive-member identity is recorded in [catalogue_provenance.json](sources/catalogue_provenance.json).

Catalogue completeness is an external input. [Frank–Dinitz's author manuscript](https://site.uvm.edu/jdinitz/files/2021/04/costasPaper.jcmcc_.pdf), p. 2, uses the complete listing through order 27, with order-13 count 12,828 in Table 3.1. Beard et al., *Costas Array Generation and Search Methodology* (2007), section IV, cites comprehensive searches through order 17 by Silverman, Vickers and Mooney, *On the number of Costas arrays as a function of array size*, Proc. IEEE 76 (1988), 851–853, [DOI](https://doi.org/10.1109/5.7156). [OEIS A008404](https://oeis.org/A008404) corroborates the full-array count and convention. Validity and distinctness alone do not establish the historical count; given that complete count, our set of that many valid distinct arrays is necessarily the full set.

Input SHA-256:

- Author PDF: `131d94036de68b755749a5edfe7a278e6581f3b163a06a5d5e040570afcdbcd0`.
- Beard archive: `a384baa41c01b4f7b4d633283125f9f471a3d1757bc863dc7136655633c9b9c2`.
- Order-13 catalogue: `a8acc2805c86001250b9104dbf41c2804cdb5734823554ac5313141e9d93e17d`.

## Method and completeness argument

The rebuilt order-13 disjointness graph has 12,828 vertices and **29,478,750 edges**, matching the paper. A k-clique is exactly a k-packing. The C++ decision search uses proper-color bounds from cell partitions of each row/column and an additional greedy independent-set partition. SAT trials use cell exact cover with a complementary hole permutation: a 12-packing leaves exactly one hole in each row and column. All SAT encodings were independently reconstructed clause-for-clause.

For symmetry, let rep(v) be the least index in v's D4 orbit. A root i has rep(i)=i and allows its neighbors j with j>i and rep(j)≥i. Every clique can be transformed by one common board symmetry so that its least vertex is the least index in the union of all its symmetry images. That clique belongs to the corresponding root. At a search node, a proper coloring orders the candidates by color then index. Every completion has a unique greatest vertex; the corresponding branch intersects its neighbors with the remaining prefix. Prefixes with fewer colors than still-required vertices are impossible. Thus all cliques are covered if every required branch and root finishes. The independent checker verifies the complete trace, including a required completion marker. Timeouts have no exclusion meaning. Full details and the trace format are in [method.md](method.md).

## Pilots and target trials so far

| Trial | Outcome | Search/verification time |
|---|---|---:|
| Full order 9, clique search | Excluded 9; 2,036 nodes | 0.011 s optimized search |
| Full order 11, clique search | Excluded 11; 1,678,389 nodes | 12.95 s initial / 8.78 s final search; 63.04 s Python / 4.15 s final C++ check |
| Full order 12 | A 12-witness | 0.003 s search |
| Order 13, CP-SAT basic / explicit holes | UNKNOWN | 300 s each |
| Order 13, Kissat sequential / binary / direct conflicts | UNKNOWN | 600 / 180 / 180 s |
| Order 13, complete clique trial | TIMEOUT: 110,379,008 nodes; sixth root unfinished | 1,500 s |

The 1,500-second trace is being continued. Replay counts reconstruct earlier work; they are not fresh search nodes. Sliced discovery trials visited every symmetry root but left cases unfinished. No complete target DRAT proof was produced; incomplete DRAT files were hashed and removed, with disposition records in `logs/`.

## Certificates and independent checkers

| File | SHA-256 |
|---|---|
{table}

All certificate files and hashes are listed in [certificates/SHA256.json](certificates/SHA256.json). Witness checks are saved in [delivered_witness_audits.json](logs/delivered_witness_audits.json).

The following commands require only Python's standard library and do not import search code:

```sh
python3 check.py certificates/witness_9_8.json --catalogue data/costas_9.txt
python3 check_clique_proof.py data/costas_9.txt certificates/no_full_9.proof.gz 9
python3 check_clique_proof.py data/costas_11.txt certificates/no_full_11.proof.gz 11
```

The additional C++ verifier is separate source: it builds the graph from cell incidences, decodes color advice by a first-fit scan, and checks every required branch without using the search's partition-selection heuristics. The search builds edges pairwise and uses both bit blocks and small sorted vectors:

```sh
clang++ -O3 -std=c++17 check_trace.cpp -lz -o check_trace
python3 check_cpp_certificate.py data/costas_11.txt certificates/no_full_11.proof.gz 11
```

Both full-trace verifier implementations reject incomplete global traces. The separate prefix checkers explicitly restrict their conclusion to the requested roots. Adversarial tests also rejected altered clauses, repeated-dot witnesses, repeated displacement vectors, invalid opcodes, and truncated gzip files. The explicit-hole and direct SAT encodings passed order-5 UNSAT pilots with independent DRAT checking by the already-installed `drat-trim`.

## What is not established

D(13) is not yet decided; timeouts, heuristic maxima, and restricted construction failures do not exclude 12. No new bound is claimed for orders 14, 15 or 17. No historical catalogue enumeration was independently re-enumerated. No complete order-13 exclusion certificate has yet passed either checker.

## Prior art and already-solved search record

Primary target: Morgan R. Frank and Jeffrey H. Dinitz, *On Maximal Partial Costas Latin Squares*, JCMCC 93 (2015), 23–32; author PDF dated 28 January 2013. It gives intervals 11–12, 12–13, 11–14, 12–16 at orders 13, 14, 15, 17. Predecessor: Dinitz, Östergård and Stinson, *Packing Costas Arrays* (2012), [arXiv:1102.1332](https://arxiv.org/abs/1102.1332).

The initial later-resolution search ran before the pilot and located no resolution. Live OpenAlex records [W2184532045](https://api.openalex.org/works/W2184532045) and [W1798634480](https://api.openalex.org/works/W1798634480) reported zero and one citing works respectively; the latter's citing work was *Signatura of magic and Latin integer squares: isentropic clans and indexing*. This is limited indexing evidence. Dinitz's later publication list, Frank-related publication results, targeted OEIS searches, and thesis leads were inspected. The linked earlier thesis PDF was unavailable.

The publisher abstract of Jin et al., [*Investigating the Existence of Costas Latin Squares via Satisfiability Testing* (SAT 2021)](https://link.springer.com/chapter/10.1007/978-3-030-80223-3_19), reports additional properties at even orders at most 10; full text was not obtained. Gulec–Abolghasemi, [arXiv:2602.03407](https://arxiv.org/abs/2602.03407), concerns construction/enumeration and has no disjoint-packing result in the saved full HTML. OEIS A008404 counts arrays, rather than maximum packings. Exact queries, access failures, qualifications and observations are in [sources/search-record.md](sources/search-record.md); raw OpenAlex responses and web captures are saved under `sources/`. No claim that all unpublished or unindexed work was excluded is made.

## Source errors and resource record

The author manuscript's Table 3.1 prints one vertex at order 2, although there are two Costas arrays and one edge. It prints 6,239 edges at order 26, exceeding the 1,540 possible pairs on 56 vertices; the independently rebuilt value is **624**. Both printed values were visually checked on [the rendered table](sources/table31.png). Reproduce with `python3 audit_source_table.py`; output is [source_table_audit.json](logs/source_table_audit.json).

All work is local to this folder. One heavy computation runs at a time; no installs, paid calls, VM work, publication or external messages were used. Guarded runs log status in [progress.md](progress.md), stop for low disk/folder limits, and preserve code hashes. The original six-hour deadline is 2026-11-10 23:41:31 UTC. Current execution state is also recorded in [next.md](next.md).
'''
Path('result.md').write_text(text)
