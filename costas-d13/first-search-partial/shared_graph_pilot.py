import os,signal,subprocess,time,json
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 for stem in ('check_trace_parallel','check_prefix_parallel'):
  subprocess.run(['clang++','-O3','-std=c++17',stem+'.cpp','-lz','-pthread','-o',stem],check=True)
 for n in (9,11):
  with open(f'logs/shared_graph_full{n}.json','w') as out,open(f'logs/shared_graph_full{n}.stderr','w') as err:
   subprocess.run(['python3','check_cpp_certificate.py',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n),'--boundaries',f'logs/parallel_{n}.boundaries.txt','--threads','3'],stdout=out,stderr=err,check=True)
  print(Path(f'logs/shared_graph_full{n}.json').read_text(),flush=True)
 for n,k in ((9,5),(11,40)):
  with open(f'logs/shared_graph_prefix{n}.json','w') as out:
   subprocess.run(['./check_prefix_parallel',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n),f'logs/prefix_parallel{n}.boundaries.txt','3',str(k)],stdout=out,check=True)
  a=json.loads(Path(f'logs/shared_graph_prefix{n}.json').read_text());b=json.loads(Path(f'logs/parallel_prefix{n}.json').read_text());assert all(a[x]==b[x] for x in ('roots','nodes','last_root_catalogue_index','scope'))
 for path in Path('logs').glob('parallel_reject_*.txt'):
  p=subprocess.run(['./check_trace_parallel','data/costas_11.txt','certificates/no_full_11.proof.gz','11',str(path),'3'],capture_output=True,text=True);assert p.returncode!=0
 for path in Path('logs').glob('parallel_reject_*.gz'):
  p=subprocess.run(['./check_trace_parallel','data/costas_9.txt',str(path),'9','logs/parallel_9.boundaries.txt','3'],capture_output=True,text=True);assert p.returncode!=0
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/shared_graph_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
