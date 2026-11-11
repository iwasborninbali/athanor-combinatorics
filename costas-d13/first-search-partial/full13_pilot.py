import os,signal,subprocess,time,json,shutil
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 prefix='logs/full13_pilot'
 with open(prefix+'.stderr','w') as err:
  subprocess.run(['./clique_early','data/costas_13.txt','13','30',prefix,'proof'],stderr=err,check=True)
 record=json.loads(Path(prefix+'.json').read_text());print(record,flush=True)
 if record['status']=='EXHAUSTED':
  certificate='certificates/no_full_13.proof.gz';shutil.copyfile(prefix+'.proof.gz',certificate)
  with open('logs/check_no_full13_cpp.json','w') as out:
   subprocess.run(['python3','check_cpp_certificate.py','data/costas_13.txt',certificate,'13'],stdout=out,check=True)
  if record['nodes']<2000000:
   with open('logs/check_no_full13_python.json','w') as out:
    subprocess.run(['python3','check_clique_proof.py','data/costas_13.txt',certificate,'13'],stdout=out,check=True)
  print('Complete order-13 upper bound D(13)<=12 independently reproduced.',flush=True)
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/full13_pilot_pause.json').write_text(json.dumps({'search_pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
