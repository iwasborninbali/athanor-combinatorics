import os, signal, subprocess, json, gzip, time
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_resume data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0]
os.kill(pid,signal.SIGSTOP)
started=time.monotonic()
try:
 for n,k in [(9,9),(11,11),(12,12)]:
  prefix=f'logs/kernel_{n}_{k}'
  with open(prefix+'.stderr','w') as err:
   subprocess.run(['./clique_kernel',f'data/costas_{n}.txt',str(k),'120',prefix,'proof'],stderr=err,check=True)
  print(Path(prefix+'.json').read_text(),flush=True)
  if n in (9,11):
   ref=f'certificates/no_full_{n}.proof.gz'
   assert gzip.open(ref,'rb').read()==gzip.open(prefix+'.proof.gz','rb').read(), 'tree differs'
  else:
   subprocess.run(['python3','check.py',prefix+'.witness.json','--catalogue',f'data/costas_{n}.txt'],check=True)
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/kernel_pilot_pause.json').write_text(json.dumps({'search_pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
