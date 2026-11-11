"""Bounded supplementary decisions, after the primary search and audit stop."""
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
from pathlib import Path

deadline=datetime(2026,11,10,23,41,31,tzinfo=timezone.utc)
assert Path('logs/target_resolved.json').exists() or Path('logs/partial_reduction13.json').exists(), 'finish primary audit first'
initial={14:(12,13),15:(11,14),17:(12,16)}
records=[];bounds={n:list(v) for n,v in initial.items()}
def remaining():return int((deadline-datetime.now(timezone.utc)).total_seconds())-300
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def guarded(name,seconds,command):
 subprocess.run(['python3','run_guarded.py','--name',name,'--seconds',str(seconds),'--']+command,check=True,stdout=subprocess.DEVNULL)
 guard=json.loads(Path(f'logs/{name}.guard.json').read_text());assert guard['returncode']==0,guard
for n in (17,14,15):
 lower,upper=bounds[n]
 while upper>lower and remaining()>180:
  k=upper;name=f'neighbour_{n}_{k}';prefix='logs/'+name
  guarded(name,45,['./clique_early',f'data/costas_{n}.txt',str(k),'30',prefix,'proof'])
  result=json.loads(Path(prefix+'.json').read_text());entry={'order':n,'target':k,'result':result};records.append(entry)
  if result['status']=='SAT':
   cert=f'certificates/witness_{n}_{k}.json';shutil.copyfile(prefix+'.witness.json',cert)
   audit=f'logs/check_neighbour_{n}_{k}.json'
   with open(audit,'w') as out:subprocess.run(['python3','check.py',cert,'--catalogue',f'data/costas_{n}.txt'],stdout=out,check=True)
   entry.update(certificate=cert,sha256=sha(cert),audit=audit,independently_checked=True);lower=k
  elif result['status']=='EXHAUSTED':
   cert=f'certificates/no_{k}_at_order{n}.proof.gz';shutil.move(prefix+'.proof.gz',cert)
   checkname=f'check_neighbour_{n}_{k}'
   guarded(checkname,remaining(),['python3','check_cpp_certificate.py',f'data/costas_{n}.txt',cert,str(k)])
   entry.update(certificate=cert,sha256=sha(cert),audit=f'logs/{checkname}.stdout',independently_checked=True);upper=k-1
   # Pure Python is an additional audit if it is cheap enough.
   projected=result['nodes']*(63.04/1678389)*1.5
   if projected<120 and projected+60<remaining():
    pyname=f'python_neighbour_{n}_{k}'
    guarded(pyname,max(30,projected*2+10),['python3','check_clique_proof.py',f'data/costas_{n}.txt',cert,str(k)])
    entry['python_audit']=f'logs/{pyname}.stdout'
  else:
   break
  bounds[n]=[lower,upper]
  Path('logs/neighbour_results.json').write_text(json.dumps({'initial_paper_intervals':initial,'final_bounds':bounds,'decisions':records},indent=2)+'\n')
  if lower==upper:break
 bounds[n]=[lower,upper]
 Path('logs/neighbour_results.json').write_text(json.dumps({'initial_paper_intervals':initial,'final_bounds':bounds,'decisions':records},indent=2)+'\n')
print(json.dumps({'bounds':bounds,'decisions':len(records)}),flush=True)
