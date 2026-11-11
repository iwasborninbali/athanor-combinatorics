"""Launch the bounded remaining target immediately after the prefix audit."""
from datetime import datetime,timezone
from pathlib import Path
import json,subprocess,time
end=datetime(2026,11,10,23,41,31,tzinfo=timezone.utc)
while not Path('logs/partial_reduction13.json').exists():
 if (end-datetime.now(timezone.utc)).total_seconds()<780:
  print('Insufficient remaining time for a new target search; retain scoped result.',flush=True);raise SystemExit(0)
 guard=Path('logs/prefix13_complete.guard.json')
 if guard.exists():
  record=json.loads(guard.read_text())
  if record['returncode']!=0:raise RuntimeError('Prefix audit did not pass; do not launch a continuation.')
 time.sleep(2)
if not Path('logs/target_resolved.json').exists() and (end-datetime.now(timezone.utc)).total_seconds()>780:
 subprocess.run(['python3','post_partial_search.py'],check=True)
else:print('No remaining target search needed or feasible.',flush=True)
