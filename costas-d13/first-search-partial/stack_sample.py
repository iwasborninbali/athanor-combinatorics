import os,signal,subprocess,time,json
from pathlib import Path
s=Path('check_trace.cpp').read_text().replace('nodes++;','nodes++; if(nodes>1000000){cout<<"{\\\"sample_nodes\\\":1000000,\\\"seconds\\\":"<<seconds()<<",\\\"complete\\\":false}\\n";exit(0);}')
Path('benchmark_stack.cpp').write_text('// PERFORMANCE ONLY: not a complete certificate check.\n#include <cstdlib>\n'+s)
subprocess.run(['clang++','-O3','-std=c++17','benchmark_stack.cpp','-lz','-o','benchmark_stack'],check=True)
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
pids=[int(row.strip().split(None,1)[0]) for row in rows if row.strip().split(None,1)[-1].startswith('./clique_resume data/costas_13.txt 12 ')]
assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 with open('logs/stack_repair_check_11.json','w') as out:
  subprocess.run(['./check_trace','data/costas_11.txt','logs/recolour_pilot11.proof.gz','11'],stdout=out,check=True)
 out=subprocess.check_output(['./benchmark_stack','data/costas_13.txt','logs/clique_long13.proof.gz','12'],text=True)
 record=json.loads(out);record['purpose']='performance sample only; not a complete exclusion check'
 Path('logs/stack_verifier_order13_sample.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
finally:
 os.kill(pid,signal.SIGCONT)
