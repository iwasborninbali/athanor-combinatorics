#!/usr/bin/env python3
import glob,hashlib,json,os,platform,subprocess,tarfile
from pathlib import Path

assert json.loads(Path('logs/isolated_status.json').read_text())['status']=='COMPLETE'
manifest=json.loads(Path('certificates/order13_manifest.json').read_text())
assert manifest['status']=='EXHAUSTED_INDEPENDENTLY_VERIFIED'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
paths=['baseline/clique_early.cpp','baseline/small_early.hpp','baseline/timed_baseline.cpp','baseline/clique_early_bench',
       'src/clique_fast.cpp','src/local_fast.hpp','src/clique_fast','checkers/check_trace.cpp','checkers/check_trace',
       'checkers/check_roots.cpp','checkers/check_roots','checkers/check_clique_proof.py','checkers/check.py','checkers/audit_speed.py',
       'merge_proof.py','stream_scope.py','finish_parallel.sh','isolated_inner.sh','summarize_isolated.py']
Path('logs/final_source_hashes.json').write_text(json.dumps({p:sha(p) for p in paths},indent=2)+'\n')
info=dict(python=platform.python_version(),python_assertions_enabled=__debug__,machine=platform.machine(),
          compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],cpus=os.cpu_count(),
          cpu_model=next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),
          flags_common='-O3 -march=native -DNDEBUG -std=c++17 -DENABLE_SMALL_KERNEL -DDISABLE_HOLE_MATCHING',
          flags_new='-DLOCAL_THRESHOLD=512',link='-lz')
Path('logs/toolchain.json').write_text(json.dumps(info,indent=2)+'\n')

def timer(p):
 d={}
 for s in Path(p).read_text().splitlines():
  for label,key in [('User time (seconds)','user_seconds'),('System time (seconds)','system_seconds'),('Maximum resident set size (kbytes)','max_rss_kb')]:
   if label+':' in s:d[key]=float(s.rsplit(': ',1)[1])
  if 'Elapsed (wall clock)' in s:
   value=s.rsplit(': ',1)[1];d['elapsed_seconds']=sum(float(v)*60**i for i,v in enumerate(reversed(value.split(':'))))
 d['cpu_seconds']=d['user_seconds']+d['system_seconds'];return d
names=['full_even','full_odd','check13_even','check13_odd','iso_old_13','iso_new_13']
t={name:timer(f'logs/{name}.time') for name in names}
t['search_cpu_hours']=sum(t[n]['cpu_seconds'] for n in ['full_even','full_odd'])/3600
t['verification_cpu_hours']=sum(t[n]['cpu_seconds'] for n in ['check13_even','check13_odd'])/3600
t['verification_thread_wall_hours']=sum(t[n]['elapsed_seconds'] for n in ['check13_even','check13_odd'])/3600
starts=[Path(f'logs/{n}.json').stat().st_mtime-json.loads(Path(f'logs/{n}.json').read_text())['seconds'] for n in ['full_even','full_odd']]
ends=[Path(f'logs/{n}.json').stat().st_mtime for n in ['full_even','full_odd']]
t['search_first_start_epoch']=min(starts);t['search_last_end_epoch']=max(ends)
t['search_staggered_span_seconds']=max(ends)-min(starts)
Path('logs/final_timing.json').write_text(json.dumps(t,indent=2)+'\n')
for i in range(1,4):assert sha(f'logs/iso_new_11_{i}.proof.gz')==sha('logs/fast512_11.proof.gz')
patterns=['logs/*.json','logs/*.roots.jsonl','logs/*.time','logs/*SHA*','logs/check13.pids','logs/active_groups.json',
          'logs/audit_balancing.jsonl','logs/isolated*.txt','logs/isolated_child.pid','logs/isolated_started.txt','logs/isolated_finished.txt',
          'logs/check13_*.stderr','logs/iso_*.stderr','logs/iso_*.proof.gz','certificates/order13_manifest.json','certificates/order13_merge_plan.json']
files=sorted({p for pattern in patterns for p in glob.glob(pattern) if Path(p).is_file() and Path(p).stat().st_size})
# Proofs for fixed samples stay on the VM; their recorded timings/counts suffice here.
files=[p for p in files if not p.endswith('.proof.gz')]
with tarfile.open('logs/final_small.tar.gz','w:gz') as out:
 for p in files:out.add(p,arcname=p,recursive=False)
print(json.dumps(dict(files=len(files),archive_bytes=Path('logs/final_small.tar.gz').stat().st_size,
                     timing=t,toolchain=info),indent=2))
