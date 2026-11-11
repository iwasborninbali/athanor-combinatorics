import os, signal, subprocess, json, time
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_resume data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 for n in (9,11):
  with open(f'logs/stack_check_{n}.json','w') as out,open(f'logs/stack_check_{n}.stderr','w') as err:
   subprocess.run(['python3','check_cpp_certificate.py',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n)],stdout=out,stderr=err,check=True)
  print(Path(f'logs/stack_check_{n}.json').read_text(),flush=True)
 with open('logs/stack_repair_check_11.json','w') as out:
  subprocess.run(['./check_trace','data/costas_11.txt','logs/recolour_11.proof.gz','11'],stdout=out,check=True)
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/verifier_stack_pilot_pause.json').write_text(json.dumps({'search_pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
