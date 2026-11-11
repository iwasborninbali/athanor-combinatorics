import os,signal,subprocess,time,json
from pathlib import Path
from check_chained13 import filter_check
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines();pids=[int(s.strip().split(None,1)[0]) for s in rows if s.strip().split(None,1)[-1].startswith('./clique_early data/costas_13.txt 12 ')];assert len(pids)==1,pids
pid=pids[0];os.kill(pid,signal.SIGSTOP);started=time.monotonic()
try:
 lines=Path('data/costas_13.txt').read_text().splitlines();n,m=map(int,lines[0].split());arrays=[tuple(map(int,line.split())) for line in lines[1:] if line.strip()]
 first=arrays[0];orbit=set();turn=first
 for t in range(4):
  orbit.add(turn);orbit.add(tuple(n-1-c for c in turn));nxt=[0]*n
  for r,c in enumerate(turn):nxt[c]=n-1-r
  turn=tuple(nxt)
 remaining=[a for a in arrays if a not in orbit]
 path=Path('logs/reduction_filter13_pilot.txt');path.write_text(f'{n} {len(remaining)}\n'+'\n'.join(' '.join(map(str,a)) for a in remaining)+'\n')
 audit=filter_check('data/costas_13.txt',str(path),1);print(audit,flush=True)
 bad=Path('logs/reduction_filter13_bad.txt');bad.write_text(f'{n} {len(remaining)-1}\n'+'\n'.join(' '.join(map(str,a)) for a in remaining[1:])+'\n')
 try:filter_check('data/costas_13.txt',str(bad),1)
 except AssertionError:pass
 else:raise AssertionError('invalid reduced catalogue was accepted')
 Path('logs/reduction_filter13_pilot.json').write_text(json.dumps({'valid':audit,'omitted_eligible_array_rejected':True},indent=2)+'\n')
finally:
 os.kill(pid,signal.SIGCONT)
 Path('logs/reduction_filter_pilot_pause.json').write_text(json.dumps({'pid':pid,'pause_seconds':time.monotonic()-started},indent=2)+'\n')
