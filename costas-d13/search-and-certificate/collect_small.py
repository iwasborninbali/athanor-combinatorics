#!/usr/bin/env python3
"""Collect completed small artifacts; excludes the large full proof and live audits."""
import glob
import tarfile
from pathlib import Path
patterns = [
 'certificates/new_*.witness.json', 'certificates/new_9_9.proof.gz',
 'logs/fast512_11.proof.gz', 'logs/fast512_11_check.json', 'logs/fast512_11_python.json',
 'logs/valid_*_check.json', 'logs/valid_9_9_*.json', 'logs/own_check*.json',
 'logs/adversarial_checks.json', 'logs/sanitized*.json', 'logs/new_13_11_check.json',
 'logs/full_even.json', 'logs/full_odd.json', 'logs/full_even.roots.jsonl', 'logs/full_odd.roots.jsonl',
 'logs/full_even.time', 'logs/full_odd.time', 'logs/full_even.stderr', 'logs/full_odd.stderr',
 'logs/production-SHA256SUMS', 'logs/input-SHA256SUMS', 'logs/trace_comparison.json',
 'logs/scope_regression11_?.json', 'logs/prefix40_comparison.json',
 'logs/precompletion_forecast.json', 'data/roots13.json',
 'logs/repeat_*_11_?.json', 'logs/sample_old13.json', 'logs/sample_old13.roots.jsonl',
 'logs/benchmark_summary.json', 'logs/merge_order13.json', 'logs/check13.pids',
]
files = sorted({name for pattern in patterns for name in glob.glob(pattern) if Path(name).stat().st_size})
with tarfile.open('logs/completed_small.tar.gz','w:gz') as target:
    for name in files:
        target.add(name,arcname=name,recursive=False)
print(len(files),'files',Path('logs/completed_small.tar.gz').stat().st_size,'bytes')
