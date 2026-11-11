"""Certify completed reduced-root work after a timeout; no global bound claimed."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,shutil,subprocess
from check_chained13 import load,filter_check
end=datetime(2026,11,10,23,39,tzinfo=timezone.utc)
assert not Path('logs/target_resolved.json').exists()
result=json.loads(Path('logs/reduced_target13.json').read_text());assert result['status']=='TIMEOUT'
prior=json.loads(Path('logs/partial_reduction13.json').read_text());reduced=prior['remaining_catalogue']
ledger=json.loads(Path('logs/reduced_target13.roots.json').read_text())['jobs'];jobs=[]
for job in ledger:
 if not job['complete_negative']:break
 assert job['ordinal']==len(jobs);jobs.append(job)
jobs=jobs[:48]
assert jobs and (end-datetime.now(timezone.utc)).total_seconds()>90
certificate='certificates/extra_initial_remaining13.proof.gz';bounds='certificates/extra_initial_remaining13.boundaries.txt'
count=0
with open(certificate,'wb') as out,open(bounds,'w') as index:
 for j,job in enumerate(jobs):
  with open(job['proof'],'rb') as src:shutil.copyfileobj(src,out)
  count+=job['nodes'];index.write(f'{j+1} {count}\n')
subprocess.run(['clang++','-O3','-std=c++17','check_prefix_parallel_stack.cpp','-lz','-pthread','-o','check_prefix_parallel_stack'],check=True)
name='check_extra_remaining13';Path('logs/'+name+'.deadline').write_text(end.isoformat()+'\n')
seconds=max(1,int((end-datetime.now(timezone.utc)).total_seconds()))
subprocess.run(['python3','run_guarded.py','--name',name,'--seconds',str(seconds),'--','./check_prefix_parallel_stack',reduced,certificate,'12',bounds,'3',str(len(jobs))],check=True,stdout=subprocess.DEVNULL)
guard=json.loads(Path('logs/'+name+'.guard.json').read_text());assert guard['returncode']==0,guard
audit=json.loads(Path('logs/'+name+'.stdout').read_text());assert audit['verified'] and audit['scope']=='specified initial canonical roots only' and audit['roots']==len(jobs)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
audit.update(catalogue_sha256=sha(reduced),proof_sha256=sha(certificate),boundaries_file=bounds,boundaries_sha256=sha(bounds),verifier_source_sha256=sha('check_prefix_parallel_stack.cpp'),verifier_binary_sha256=sha('check_prefix_parallel_stack'))
Path('logs/extra_prefix13_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
n,arrays=load(reduced);lookup={a:i for i,a in enumerate(arrays)};representatives=[]
for a in arrays:
 images=[];turn=a
 for t in range(4):
  images.append(lookup[turn]);images.append(lookup[tuple(n-1-c for c in turn)]);nxt=[0]*n
  for r,c in enumerate(turn):nxt[c]=n-1-r
  turn=tuple(nxt)
 representatives.append(min(images))
last=audit['last_root_catalogue_index'];remaining=[a for a,r in zip(arrays,representatives) if r>last]
path='data/costas_13_remaining_after_extra.txt'
Path(path).write_text(f'{n} {len(remaining)}\n'+'\n'.join(' '.join(map(str,a)) for a in remaining)+'\n')
combined=prior['completed_roots']+len(jobs)
relation=filter_check('data/costas_13.txt',path,combined)
record={'scope':'two scoped exclusions only; no global D(13) bound','certificate':certificate,'audit':'logs/extra_prefix13_audit.json','input_catalogue':reduced,'input_reduction_audit':'logs/reduction13_independent_check.json','additional_roots':len(jobs),'combined_original_initial_roots':combined,'remaining_catalogue':path,'remaining_vertices':len(remaining),'remaining_catalogue_sha256':sha(path),'independent_combined_filter_check':relation}
Path('logs/extended_partial_reduction13.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
