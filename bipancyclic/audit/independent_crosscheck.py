"""Compare independent kernel edge-subset enumeration to original-graph DFS."""
import collections
import itertools
import json
from pathlib import Path
import random
import subprocess
import time

from independent_witnesses import cycles


if __name__ == "__main__":
    start=time.process_time()
    rng=random.Random(20261111)
    examples=[]
    for row in json.loads(Path('../a03-bipancyclic/witnesses.json').read_text()):
        if 0<len(row['chords'])<=4:
            examples.append((row['N'],row['chords']))
    for _ in range(100):
        n=rng.choice(range(8,41,2))
        k=rng.choice(range(1,5))
        pairs=[(a,b) for a in range(n) for b in range(a+1,n)
               if (a-b)%2 and b-a not in (1,n-1)]
        examples.append((n,rng.sample(pairs,k)))
    for n,chords in examples:
        args=['./independent_exhaustive','spectrum',str(n)]
        args.extend(str(v) for edge in chords for v in edge)
        kernel=json.loads(subprocess.check_output(args,text=True))
        original={str(k):v for k,v in collections.Counter(map(len,cycles(n,chords))).items()}
        assert kernel==original,(n,chords,kernel,original)
    found=[]
    for line in Path('independent_runs.jsonl').read_text().splitlines():
        row=json.loads(line)
        if row['kind']!='solution':
            continue
        positions=[0]+list(itertools.accumulate(row['arcs']))[:-1]
        chords=[(positions[u],positions[v]) for u,v in row['endpoint_chords']]
        spectrum=collections.Counter(map(len,cycles(row['N'],chords)))
        assert set(spectrum)==set(range(4,row['N']+1,2))
        found.append(dict(N=row['N'],chords=chords,cycle_histogram=dict(spectrum)))
    result=dict(crosschecked_graphs=len(examples),random_seed=20261111,
                rediscovered_positive_graphs=found,cpu_seconds=time.process_time()-start)
    Path('independent_crosschecks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
