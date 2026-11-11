#!/usr/bin/env python3
import json
import statistics
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def lines(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s]

result = {'conditions': 'Sequential single-core runs pinned to CPU 3; no other heavy programme jobs; background load recorded; same compiler, frozen binaries, original catalogue/order and global gzip trace output.'}
pairs = []
for i in range(1,4):
    a,b=[load(f'logs/iso_{k}_11_{i}.json') for k in ['old','new']]
    assert a['status']==b['status']=='EXHAUSTED' and a['nodes']==b['nodes']==1678389
    pairs.append(dict(repeat=i,nodes=a['nodes'],old_seconds=a['seconds'],new_seconds=b['seconds']))
result['order11']=pairs
result['order11_medians']={k:statistics.median(r[k] for r in pairs) for k in ['old_seconds','new_seconds']}
result['order11_medians']['speedup']=result['order11_medians']['old_seconds']/result['order11_medians']['new_seconds']
a,b=[load(f'logs/iso_{k}_13.json') for k in ['old','new']]
assert a['status']==b['status']=='EXHAUSTED' and a['roots']==b['roots']==8 and a['nodes']==b['nodes']
old,new=[lines(f'logs/iso_{k}_13.roots.jsonl') for k in ['old','new']]
assert [r['ordinal'] for r in old]==[0,20,40,80,160,320,640,1280]
rows=[]
for x,y in zip(old,new):
    assert x['complete'] and y['complete'] and x['ordinal']==y['ordinal'] and x['vertex']==y['vertex'] and x['nodes']==y['nodes']
    rows.append(dict(ordinal=x['ordinal'],vertex=x['vertex'],nodes=x['nodes'],old_seconds=x['seconds'],new_seconds=y['seconds'],speedup=x['seconds']/y['seconds']))
result['order13_sample']=rows
result['order13_totals']=dict(nodes=a['nodes'],old_seconds=a['seconds'],new_seconds=b['seconds'],speedup=a['seconds']/b['seconds'])
run=load('certificates/order13_manifest.json')
assert run['status']=='EXHAUSTED_INDEPENDENTLY_VERIFIED'
us=a['seconds']/a['nodes']
large=[r for r in rows if r['nodes']>=100000]
observed=[r['old_seconds']/r['nodes'] for r in large]
# A deterministic scenario band; it is not a statistical confidence interval.
repeat_variation=max(abs(r['old_seconds']/result['order11_medians']['old_seconds']-1) for r in pairs)
padding=max(.15,repeat_variation)
result['full_estimates']=dict(nodes=run['nodes'],new_measured_core_hours=run['search_core_seconds']/3600,
    old_estimated_core_hours=run['nodes']*us/3600,
    old_scenario_core_hours=[run['nodes']*min(observed)*(1-padding)/3600,run['nodes']*max(observed)*(1+padding)/3600],
    scenario_padding=padding,
    caveat='Old estimate uses the sample weighted seconds/state. Scenario takes observed per-state extremes from sampled roots with >=100k states plus at least 15% padding; not a confidence interval or mathematical bound.')
def cpu(path):
    line=next(s for s in Path(path).read_text().splitlines() if s.startswith('cpu3 '))
    return list(map(int,line.split()[1:]))
start,end=cpu('logs/isolated_cpu_before.txt'),cpu('logs/isolated_cpu_after.txt')
delta=[b-a for a,b in zip(start,end)]
result['cpu3_counters_delta']=delta
result['cpu3_steal_fraction']=delta[7]/sum(delta[:8])
Path('logs/isolated_benchmark_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
