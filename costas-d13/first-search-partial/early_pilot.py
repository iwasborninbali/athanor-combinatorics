import os,signal,subprocess,time,json,gzip
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_vector data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 with open('logs/early_resume9.stderr','w') as err:
  subprocess.run(['./clique_early','data/costas_9.txt','9','120','logs/early_resume9','resume','logs/resume_9_prefix.proof.gz'],stderr=err,check=True)
 subprocess.run(['./check_trace','data/costas_9.txt','logs/early_resume9.proof.gz','9'],check=True)
 with open('logs/early_pilot11.stderr','w') as err:
  subprocess.run(['./clique_early','data/costas_11.txt','11','120','logs/early_pilot11','proof'],stderr=err,check=True)
 with open('logs/early_check11.json','w') as out:
  subprocess.run(['./check_trace','data/costas_11.txt','logs/early_pilot11.proof.gz','11'],stdout=out,check=True)
 print(Path('logs/early_pilot11.json').read_text(),flush=True)
 with open('logs/early_trial13.stderr','w') as err:
  subprocess.run(['./clique_early','data/costas_13.txt','12','30','logs/early_trial13','proof'],stderr=err,check=True)
 print(Path('logs/early_trial13.json').read_text(),flush=True)

finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/early_target_pilot_pause.json').write_text(json.dumps({'search_pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
