"""Collect explicit small-order witnesses and a five-chord extension family."""
import json
from pathlib import Path
import subprocess
from check_witnesses import enumerate_cycles

ROOT = Path(__file__).resolve().parent
LOGS = ROOT/'logs'
LOGS.mkdir(exist_ok=True)
out = [{'N':4, 'chords':[]}]
for n in range(6, 47, 2):
    k = 1 if n<=8 else 2 if n<=14 else 3 if n<=26 else 4
    if not (ROOT/f'patterns{k}.txt').exists():
        subprocess.run(['python3','export_patterns.py','--chords',str(k)],check=True,cwd=ROOT)
    p = subprocess.run([str(ROOT/'exhaustive'),f'patterns{k}.txt',str(n)],capture_output=True,text=True,cwd=ROOT)
    (LOGS/f'positive_k{k}_n{n}.jsonl').write_text(p.stderr)
    assert p.returncode == 10, (n,k,p.returncode,p.stderr[-1000:])
    witness = json.loads(p.stderr.splitlines()[-1])
    item = {'N':n, 'chords':witness['chords']}
    counts, _ = enumerate_cycles(n,item['chords'])
    assert set(counts) == set(range(4,n+1,2)), (n,counts)
    out.append(item)
    print(json.dumps(item),flush=True)

# This particular independently verified 46-vertex graph has an edge (5,6)
# on a cycle of each even length 30..46. Subdivide that edge by any even
# number d<=18 of new vertices and retain the original edge as a chord.
base = [[0,5],[0,43],[1,38],[26,45]]
out[-1]['chords'] = base
for n in range(48,65,2):
    delta = n-46
    mapping = lambda v: v if v<=5 else v+delta
    chords = [[mapping(u),mapping(v)] for u,v in base]
    chords.append([5,6+delta])
    item = {'N':n,'chords':sorted(sorted(e) for e in chords)}
    counts,_ = enumerate_cycles(n,item['chords'])
    assert set(counts) == set(range(4,n+1,2)), (n,counts)
    out.append(item)
    print(json.dumps(item),flush=True)
(ROOT/'witnesses.json').write_text(json.dumps(out,indent=2)+'\n')
