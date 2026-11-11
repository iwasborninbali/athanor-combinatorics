import os,signal,subprocess,time,json,re
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 subprocess.run(['clang++','-O3','-std=c++17','benchmark_parallel13.cpp','-lz','-pthread','-o','benchmark_parallel13'],check=True)
 pairs=[(int(k),int(v)) for k,v in re.findall(r'roots=(\d+).*?nodes=(\d+)',Path('logs/clique_early13.stderr').read_text()) if int(k)<=60]
 assert len(pairs)==3
 path=Path('logs/parallel_target_benchmark.boundaries.txt');path.write_text(''.join(f'{k} {v}\n' for k,v in pairs))
 out=subprocess.check_output(['./benchmark_parallel13','data/costas_13.txt','logs/clique_early13.proof.gz','12',str(path),'3','60'],text=True,timeout=30)
 record=json.loads(out);assert record['complete'] is False and record['sample_nodes']==3000000
 record['conservative_speedup_vs_serial_sample']=3*2.8303/max(record['verification_seconds_by_thread'])
 Path('logs/parallel_target_benchmark.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/parallel_target_benchmark_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
