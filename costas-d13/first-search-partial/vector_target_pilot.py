import os,signal,subprocess,time,json,gzip
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_resume data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 with open('logs/vector_resume9.stderr','w') as err:
  subprocess.run(['./clique_vector','data/costas_9.txt','9','120','logs/vector_resume9','resume','logs/resume_9_prefix.proof.gz'],stderr=err,check=True)
 assert gzip.open('logs/vector_resume9.proof.gz','rb').read()==gzip.open('certificates/no_full_9.proof.gz','rb').read()
 with open('logs/vector_trial13.stderr','w') as err:
  subprocess.run(['./clique_vector','data/costas_13.txt','12','30','logs/vector_trial13','proof'],stderr=err,check=True)
 print(Path('logs/vector_trial13.json').read_text(),flush=True)
 tests={
  'no_marker':gzip.open('certificates/no_full_9.proof.gz','rb').read()[:-8],
  'invalid_opcode':b'\xff'+gzip.open('certificates/no_full_9.proof.gz','rb').read()[1:],
  'valid_prefix':gzip.open('certificates/no_full_9.proof.gz','rb').read()[:100],
 }
 result=[]
 for name,data in tests.items():
  file=Path(f'logs/reject_stack_{name}.gz');file.write_bytes(gzip.compress(data))
  p=subprocess.run(['./check_trace','data/costas_9.txt',str(file),'9'],capture_output=True,text=True)
  assert p.returncode!=0,(name,p.stdout,p.stderr)
  result.append({'case':name,'returncode':p.returncode,'stderr':p.stderr.strip()})
 Path('logs/stack_verifier_rejections.json').write_text(json.dumps(result,indent=2)+'\n')
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/vector_target_pilot_pause.json').write_text(json.dumps({'search_pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
