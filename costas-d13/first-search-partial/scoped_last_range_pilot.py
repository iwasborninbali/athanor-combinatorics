import os,signal,subprocess,time,json
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 subprocess.run(['clang++','-O3','-std=c++17','check_prefix_parallel.cpp','-lz','-pthread','-o','check_prefix_parallel'],check=True)
 Path('logs/prefix_parallel9_loose.boundaries.txt').write_text('5 2036\n')
 with open('logs/prefix_parallel9_loose.json','w') as out:
  subprocess.run(['./check_prefix_parallel','data/costas_9.txt','certificates/no_full_9.proof.gz','9','logs/prefix_parallel9_loose.boundaries.txt','3','5'],stdout=out,check=True)
 a=json.loads(Path('logs/prefix_parallel9_loose.json').read_text());b=json.loads(Path('logs/prefix_python9_5.json').read_text());assert all(a[k]==b[k] for k in ('roots','nodes','last_root_catalogue_index','consumed_trace_bytes'));print(a,flush=True)
 Path('logs/prefix_parallel9_short.boundaries.txt').write_text('5 200\n')
 p=subprocess.run(['./check_prefix_parallel','data/costas_9.txt','certificates/no_full_9.proof.gz','9','logs/prefix_parallel9_short.boundaries.txt','3','5'],capture_output=True,text=True);assert p.returncode!=0
 with open('logs/prefix_parallel11_latest.json','w') as out:
  subprocess.run(['./check_prefix_parallel','data/costas_11.txt','certificates/no_full_11.proof.gz','11','logs/prefix_parallel11.boundaries.txt','3','40'],stdout=out,check=True)
 c=json.loads(Path('logs/prefix_parallel11_latest.json').read_text());assert c['nodes']==1182263 and c['roots']==40 and c['consumed_trace_bytes']==1182263
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/scoped_last_range_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
