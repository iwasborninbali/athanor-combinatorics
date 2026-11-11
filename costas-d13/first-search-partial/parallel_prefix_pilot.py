import os,signal,subprocess,time,json
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 Path('logs/prefix_parallel9.boundaries.txt').write_text('5 613\n')
 Path('logs/prefix_parallel11.boundaries.txt').write_text('20 736462\n40 1182263\n')
 for n,k in ((9,5),(11,40)):
  with open(f'logs/parallel_prefix{n}.json','w') as out,open(f'logs/parallel_prefix{n}.stderr','w') as err:
   subprocess.run(['./check_prefix_parallel',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n),f'logs/prefix_parallel{n}.boundaries.txt','3',str(k)],stdout=out,stderr=err,check=True)
  record=json.loads(Path(f'logs/parallel_prefix{n}.json').read_text());assert record['verified'] and record['roots']==k and record['scope']=='specified initial canonical roots only';print(record,flush=True)
  if n==9:other=json.loads(Path('logs/prefix_python9_5.json').read_text())
  else:other=json.loads(subprocess.check_output(['./check_root_prefix',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n),str(k)],text=True))
  for key in ('roots','nodes','last_root_catalogue_index'):assert record[key]==other[key]
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/parallel_prefix_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
