"""Spend remaining authorised time on the exact reduced target, before neighbours."""
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess
from pathlib import Path
from check_chained13 import filter_check

deadline=datetime(2026,11,10,23,41,31,tzinfo=timezone.utc)
assert not Path('logs/target_resolved.json').exists()
partial=json.loads(Path('logs/partial_reduction13.json').read_text());first=json.loads(Path(partial['audit']).read_text());assert first['verified'] and first['scope']=='specified initial canonical roots only'
k=first['roots'];reduced=partial['remaining_catalogue'];relation=filter_check('data/costas_13.txt',reduced,k)
Path('logs/reduction13_independent_check.json').write_text(json.dumps(relation,indent=2)+'\n')
def remaining():return int((deadline-datetime.now(timezone.utc)).total_seconds())-300
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert sha(partial['certificate'])==first['proof_sha256']
assert relation['original_catalogue_sha256']==first['catalogue_sha256']
assert remaining()>480
cap=min(1500,max(120,int((remaining()-180)*0.65)))
name='reduced_target13';prefix='logs/'+name
Path(prefix+'.time-limit').write_text(str(cap)+'\n')
subprocess.run(['python3','run_guarded.py','--name',name,'--seconds',str(min(cap+140,remaining()-180)),'--','./clique_threaded',reduced,'12',str(cap),prefix,'3'],check=True,stdout=subprocess.DEVNULL)
guard=json.loads(Path(prefix+'.guard.json').read_text());assert guard['returncode']==0,guard
result=json.loads(Path(prefix+'.json').read_text());print(json.dumps(result),flush=True)
if result['status']=='SAT':
 witness=json.loads(Path(prefix+'.witness.json').read_text())
 rows=[tuple(map(int,s.split())) for s in Path('data/costas_13.txt').read_text().splitlines()[1:] if s.strip()];lookup={a:i for i,a in enumerate(rows)}
 witness['catalogue_row_indices']=[lookup[tuple(a)] for a in witness['arrays']]
 cert='certificates/witness_13_12.json';Path(cert).write_text(json.dumps(witness,indent=2)+'\n');audit='logs/check_witness_13_12.json'
 with open(audit,'w') as out:subprocess.run(['python3','check.py',cert,'--catalogue','data/costas_13.txt'],stdout=out,check=True)
 Path('logs/target_resolved.json').write_text(json.dumps({'kind':'12-packing','certificate':cert,'audit':audit,'discovery':'exact reduced-catalogue continuation'},indent=2)+'\n')
elif result['status']=='EXHAUSTED':
 cert='certificates/no_12_in_remaining13.proof.gz';shutil.move(prefix+'.proof.gz',cert)
 pairs=[(int(root),int(offset)) for root,offset in re.findall(r'roots=(\d+).*?nodes=(\d+)',Path(prefix+'.stderr').read_text())]
 if not pairs or pairs[-1]!=(result['roots'],result['nodes']):pairs.append((result['roots'],result['nodes']))
 bounds='certificates/remaining13.boundaries.txt'
 if Path(prefix+'.boundaries.txt').exists():shutil.copyfile(prefix+'.boundaries.txt',bounds)
 else:Path(bounds).write_text(''.join(f'{root} {offset}\n' for root,offset in pairs))
 assert remaining()>0
 subprocess.run(['python3','run_guarded.py','--name','check_reduced_target13','--seconds',str(remaining()),'--','python3','check_cpp_certificate.py',reduced,cert,'12','--boundaries',bounds,'--threads','3'],check=True,stdout=subprocess.DEVNULL)
 guard=json.loads(Path('logs/check_reduced_target13.guard.json').read_text());assert guard['returncode']==0,guard
 second=json.loads(Path('logs/check_reduced_target13.stdout').read_text());assert second['verified'] and second['roots']==relation['remaining_roots'] and second['excluded_clique_size']==12
 assert second['catalogue_sha256']==relation['remaining_catalogue_sha256']
 record={'kind':'chained no 12-packing','certificate':partial['certificate'],'audit':partial['audit'],'tail_certificate':cert,'tail_audit':'logs/check_reduced_target13.stdout','reduced_catalogue':reduced,'reduction_audit':'logs/reduction13_independent_check.json','prefix_roots':k,'standalone_python_checker':'check_chained13.py'}
 Path('logs/target_resolved.json').write_text(json.dumps(record,indent=2)+'\n');print('Complete two-certificate exclusion independently checked.',flush=True)
else:print('Reduced continuation incomplete; no global bound follows.',flush=True)
