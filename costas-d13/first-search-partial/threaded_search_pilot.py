import os,signal,subprocess,time,json,gzip
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 subprocess.run(['clang++','-O3','-std=c++17','-DDISABLE_HOLE_MATCHING','-DENABLE_SMALL_KERNEL','clique_threaded.cpp','-lz','-pthread','-o','clique_threaded'],check=True)
 for n in (9,11,12):
  prefix=f'logs/threaded_pilot{n}'
  with open(prefix+'.stderr','w') as err:subprocess.run(['./clique_threaded',f'data/costas_{n}.txt',str(n),'90',prefix,'3'],stderr=err,check=True)
  record=json.loads(Path(prefix+'.json').read_text());print(record,flush=True)
  if n==9:
   with open('logs/threaded_serial9.stderr','w') as err:subprocess.run(['./clique_early','data/costas_9.txt','9','90','logs/threaded_serial9','proof'],stderr=err,check=True)
   expected='logs/threaded_serial9.proof.gz'
  elif n==11:expected='logs/early_pilot11.proof.gz'
  else:
   subprocess.run(['python3','check.py',prefix+'.witness.json','--catalogue',f'data/costas_{n}.txt'],check=True);continue
  assert record['status']=='EXHAUSTED'
  assert gzip.open(prefix+'.proof.gz','rb').read()==gzip.open(expected,'rb').read(),'parallel search tree differs'
  with open(prefix+'.audit.json','w') as out:subprocess.run(['python3','check_cpp_certificate.py',f'data/costas_{n}.txt',prefix+'.proof.gz',str(n),'--boundaries',prefix+'.boundaries.txt','--threads','3'],stdout=out,check=True)
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/threaded_search_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
