"""Audit a restricted root prefix after a normal target timeout.
This NEVER claims D(13) or global nonexistence of a 12-packing.
"""
from datetime import datetime, timezone
import hashlib,json,shutil,subprocess,re
from pathlib import Path

deadline=datetime(2026,11,10,23,41,31,tzinfo=timezone.utc)
result=json.loads(Path('logs/clique_early13.json').read_text())
assert result['status']=='TIMEOUT' and result['cut_roots']==0
completed=result['roots']-1
assert completed>0
pairs=[(int(root),int(offset)) for root,offset in re.findall(r'roots=(\d+).*?nodes=(\d+)',Path('logs/clique_early13.stderr').read_text()) if int(root)<=completed]
assert pairs
count=completed
if pairs[-1][0]!=count:pairs.append((count,result['nodes']-1))
certificate=Path('certificates/excluded_initial_roots13.proof.gz')
source=Path('logs/clique_early13.proof.gz')
if source.exists():shutil.move(source,certificate)
seconds=int((deadline-datetime.now(timezone.utc)).total_seconds())-300
assert seconds>0
boundaries=Path('certificates/excluded_initial_roots13.boundaries.txt')
boundaries.write_text(''.join(f'{root} {offset}\n' for root,offset in pairs))
command=['./check_prefix_parallel','data/costas_13.txt',str(certificate),'12',str(boundaries),'3',str(count)]
subprocess.run(['python3','run_guarded.py','--name','prefix13_complete','--seconds',str(seconds),'--']+command,check=True)
guard=json.loads(Path('logs/prefix13_complete.guard.json').read_text())
assert guard['returncode']==0,guard
audit=json.loads(Path('logs/prefix13_complete.stdout').read_text())
assert audit['verified'] and audit['scope']=='specified initial canonical roots only' and audit['roots']==count and audit['order']==13 and audit['excluded_size_in_these_roots']==12

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
audit.update(catalogue_sha256=sha('data/costas_13.txt'),proof_sha256=sha(certificate),verifier_source_sha256=sha('check_prefix_parallel.cpp'),verifier_binary_sha256=sha('check_prefix_parallel'),boundaries_file=str(boundaries),boundaries_sha256=sha(boundaries),backend='parallel root ranges')
Path('logs/prefix13_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
# Independent orbit computation for the explicit induced-subgraph reduction.
lines=Path('data/costas_13.txt').read_text().splitlines();n,m=map(int,lines[0].split());arrays=[tuple(map(int,line.split())) for line in lines[1:] if line.strip()];index={v:i for i,v in enumerate(arrays)}
representatives=[]
for v in arrays:
 images=[]
 for transpose in (False,True):
  for rr in (False,True):
   for cc in (False,True):
    image=[0]*n
    for r,c in enumerate(v):
     x,y=(c,r) if transpose else (r,c)
     if rr:x=n-1-x
     if cc:y=n-1-y
     image[x]=y
    images.append(index[tuple(image)])
 representatives.append(min(images))
last=audit['last_root_catalogue_index'];remaining=[i for i,rep in enumerate(representatives) if rep>last]
reduced=Path('data/costas_13_remaining.txt')
with reduced.open('w') as f:
 f.write(f'{n} {len(remaining)}\n')
 for i in remaining:f.write(' '.join(map(str,arrays[i]))+'\n')
record={'scope':'restricted roots only; no global D(13) bound','certificate':str(certificate),'audit':'logs/prefix13_audit.json','completed_roots':count,'last_excluded_representative_index':last,'removed_vertices':m-len(remaining),'remaining_vertices':len(remaining),'remaining_catalogue':str(reduced),'remaining_catalogue_sha256':sha(reduced),'remaining_original_indices':remaining,'statement':'Every hypothetical 12-packing is entirely contained in the induced subgraph on arrays whose original D4 representative index is greater than the recorded last excluded index.'}
Path('logs/partial_reduction13.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='remaining_original_indices'},indent=2),flush=True)
