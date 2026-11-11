#!/usr/bin/env python3
"""Summarise fixed-root measurements, retaining scope and extrapolation limits."""
import hashlib
import json
import statistics
from pathlib import Path

SAMPLE = [0, 20, 40, 80, 160, 320, 640, 1280]
base = Path('.')

def load(path):
    return json.loads(Path(path).read_text())

def lines(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text().splitlines() if x] if p.exists() else []

old = {r['ordinal']: r for r in lines('logs/sample_old13.roots.jsonl')}
new = {r['ordinal']: r for name in ['full_even', 'full_odd'] for r in lines(f'logs/{name}.roots.jsonl')}
rows = []
for ordinal in SAMPLE:
    if ordinal not in old or ordinal not in new:
        continue
    a, b = old[ordinal], new[ordinal]
    assert a['complete'] and b['complete'] and a['vertex'] == b['vertex'] and a['nodes'] == b['nodes']
    rows.append(dict(ordinal=ordinal, vertex=a['vertex'], nodes=a['nodes'], old_seconds=a['seconds'],
                     new_seconds=b['seconds'], speedup=a['seconds']/b['seconds']))
paired = []
for i in range(1, 4):
    a, b = load(f'logs/repeat_old_11_{i}.json'), load(f'logs/repeat_new_11_{i}.json')
    assert a['status'] == b['status'] == 'EXHAUSTED' and a['nodes'] == b['nodes'] == 1678389
    paired.append(dict(repeat=i, nodes=a['nodes'], old_seconds=a['seconds'], new_seconds=b['seconds']))
report = dict(sample_ordinals=SAMPLE, order11=paired, order13_sample=rows,
              sample_complete=len(rows) == len(SAMPLE),
              completed_new_roots=len(new), completed_new_nodes=sum(r['nodes'] for r in new.values()))
if rows:
    report['sample_totals'] = dict(nodes=sum(r['nodes'] for r in rows), old_seconds=sum(r['old_seconds'] for r in rows),
                                   new_seconds=sum(r['new_seconds'] for r in rows))
    report['sample_totals']['speedup'] = report['sample_totals']['old_seconds']/report['sample_totals']['new_seconds']
if Path('certificates/order13_manifest.json').exists() and len(rows) == len(SAMPLE):
    run = load('certificates/order13_manifest.json')
    sample = report['sample_totals']
    us = sample['old_seconds']/sample['nodes']*1e6
    meaningful = [r for r in rows if r['nodes'] >= 100000]
    observed = [r['old_seconds']/r['nodes'] for r in meaningful]
    # An explicit empirical scenario band, not a statistical confidence interval.
    median_old11 = statistics.median(r['old_seconds'] for r in paired)
    variation = max(abs(r['old_seconds']/median_old11-1) for r in paired)
    padding = max(.15, variation)
    report['complete_run'] = dict(nodes=run['nodes'], roots=run['roots'],
         new_core_hours=run['search_core_seconds']/3600,
         old_estimated_core_hours=run['nodes']*us/1e6/3600,
         old_scenario_core_hours=[run['nodes']*min(observed)*(1-padding)/3600,
                                  run['nodes']*max(observed)*(1+padding)/3600],
         uncertainty='Observed old per-node extremes on sample roots >=100k states, expanded by max(15%, observed old order-11 repeat variation); not a confidence interval or bound.',
         new_root_core_seconds=sum(r['seconds'] for r in new.values()),
         max_root_seconds=max(r['seconds'] for r in new.values()),
         max_root_ordinal=max(new, key=lambda q: new[q]['seconds']))
Path('logs/benchmark_summary.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
