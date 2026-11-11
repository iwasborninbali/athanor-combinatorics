import os,signal,subprocess,time,json,re,gzip
from pathlib import Path
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 for n in (9,11):
  if n==11:
   pairs=[(int(k),int(v)) for k,v in re.findall(r'roots=(\d+).*?nodes=(\d+)',Path('logs/early_pilot11.stderr').read_text())]
   pairs.append((555,1678389))
  else:
   pairs=[(100,2036)]
  bounds=Path(f'logs/parallel_{n}.boundaries.txt');bounds.write_text(''.join(f'{k} {v}\n' for k,v in pairs))
  with open(f'logs/parallel_check_{n}.json','w') as out,open(f'logs/parallel_check_{n}.stderr','w') as err:
   subprocess.run(['./check_trace_parallel',f'data/costas_{n}.txt',f'certificates/no_full_{n}.proof.gz',str(n),str(bounds),'3'],stdout=out,stderr=err,check=True)
  print(Path(f'logs/parallel_check_{n}.json').read_text(),flush=True)
 tests=[]
 base=Path('logs/parallel_11.boundaries.txt').read_text()
 variants={'bad_offset':base.replace('20 736462','20 736463'),'missing_roots':base.rsplit('\n',2)[0]+'\n','bad_root_ordinal':base.replace('40 1182263','41 1182263'),'malformed':base+'x\n'}
 for label,data in variants.items():
  path=Path(f'logs/parallel_reject_{label}.txt');path.write_text(data)
  run=subprocess.run(['./check_trace_parallel','data/costas_11.txt','certificates/no_full_11.proof.gz','11',str(path),'3'],capture_output=True,text=True)
  assert run.returncode!=0,(label,run.stdout)
  tests.append({'case':label,'rejected':True,'stderr':run.stderr[-300:]})
 raw=gzip.open('certificates/no_full_9.proof.gz','rb').read()
 for label,data in [('no_completion',raw[:-8]),('invalid_opcode',b'\xff'+raw[1:])]:
  path=Path(f'logs/parallel_reject_{label}.gz');path.write_bytes(gzip.compress(data))
  run=subprocess.run(['./check_trace_parallel','data/costas_9.txt',str(path),'9','logs/parallel_9.boundaries.txt','3'],capture_output=True,text=True);assert run.returncode!=0;tests.append({'case':label,'rejected':True,'stderr':run.stderr[-300:]})
 path=Path('logs/parallel_reject_gzip_footer.gz');path.write_bytes(Path('certificates/no_full_9.proof.gz').read_bytes()[:-5]);run=subprocess.run(['./check_trace_parallel','data/costas_9.txt',str(path),'9','logs/parallel_9.boundaries.txt','3'],capture_output=True,text=True);assert run.returncode!=0;tests.append({'case':'truncated gzip footer','rejected':True,'stderr':run.stderr[-300:]})
 Path('logs/parallel_checker_rejections.json').write_text(json.dumps(tests,indent=2)+'\n')
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/parallel_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
