#!/usr/bin/env python3
"""Record deterministic interpolation scenarios before seeing the full result."""
import datetime
import json
import math
from pathlib import Path
sample = [json.loads(s) for s in Path('logs/sample_old13.roots.jsonl').read_text().splitlines()]
assert len(sample) == 8 and all(x['complete'] for x in sample)
count = json.loads(Path('data/roots13.json').read_text())['count']
estimates = {}
for model in ['linear', 'log_linear']:
    values = []
    for ordinal in range(count):
        left = max((x for x in sample if x['ordinal'] <= ordinal), key=lambda x: x['ordinal'])
        right = min((x for x in sample if x['ordinal'] >= ordinal), key=lambda x: x['ordinal'], default=left)
        if left['ordinal'] == right['ordinal']:
            value = left['nodes']
        else:
            t = (ordinal - left['ordinal']) / (right['ordinal'] - left['ordinal'])
            if model == 'linear':
                value = (1-t)*left['nodes'] + t*right['nodes']
            else:
                value = math.exp((1-t)*math.log(left['nodes']) + t*math.log(right['nodes']))
        values.append(value)
    estimates[model] = dict(nodes=sum(values), first40_nodes=sum(values[:40]))
nodes = [x['nodes'] for x in estimates.values()]
result = dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), roots=count,
              sample=sample, interpolation=estimates,
              wider_planning_scenario=[min(nodes)*.75, max(nodes)*1.25],
              qualification='Deterministic interpolation scenarios, not confidence intervals or bounds. Declining tail and the absence of unseen expensive late roots are assumptions. Padding is a declared planning choice, not a measured probability.')
Path('logs/precompletion_forecast.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='sample'},indent=2))
