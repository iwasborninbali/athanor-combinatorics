"""Optional additional pure-Python audit of one target root, never a global claim."""
from datetime import datetime,timezone
import json,subprocess
from pathlib import Path
end=datetime(2026,11,10,23,41,31,tzinfo=timezone.utc)
seconds=int((end-datetime.now(timezone.utc)).total_seconds())-600
assert seconds>=1500,'leave adequate time; skip this optional audit otherwise'
p=Path('logs/target_resolved.json')
if p.exists():
 result=json.loads(p.read_text());assert result['kind'] in ('no 12-packing','chained no 12-packing');certificate=result['certificate']
else:
 result=json.loads(Path('logs/partial_reduction13.json').read_text());certificate=result['certificate']
subprocess.run(['python3','run_guarded.py','--name','python_target_root1','--seconds',str(seconds),'--','python3','check_clique_prefix.py','data/costas_13.txt',certificate,'12','1'],check=True,stdout=subprocess.DEVNULL)
guard=json.loads(Path('logs/python_target_root1.guard.json').read_text())
if guard['returncode']==0:
 audit=json.loads(Path('logs/python_target_root1.stdout').read_text());assert audit['verified'] and audit['roots']==1 and audit['scope']=='specified initial canonical roots only'
 print(json.dumps(audit),flush=True)
else:
 print(json.dumps(guard),flush=True)
 if guard['stop_reason']=='finished':raise RuntimeError('logical checker failure; investigate before claiming a result')
