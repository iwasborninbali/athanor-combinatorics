#!/usr/bin/env python3
"""Schedule the requested fair baseline comparison, within the same deadline."""
import datetime
import json
import subprocess
import time
from pathlib import Path
end=datetime.datetime(2026,11,11,3,8,tzinfo=datetime.timezone.utc).timestamp()
while time.time()<end:
    p=Path('certificates/order13_manifest.json')
    try:
        ready=p.exists() and json.loads(p.read_text())['status']=='EXHAUSTED_INDEPENDENTLY_VERIFIED'
    except (OSError,ValueError,KeyError):
        ready=False
    if ready:
        break
    time.sleep(min(20,max(1,end-time.time())))
remaining=int(end-time.time())
if remaining<1800:
    record=dict(status='SKIPPED_DEADLINE',remaining_seconds=remaining)
else:
    with open('logs/isolated_benchmark.log','w') as log:
        run=subprocess.Popen(['timeout','--signal=TERM','--kill-after=5',f'{remaining}s','bash','isolated_inner.sh'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
        Path('logs/isolated_child.pid').write_text(str(run.pid)+'\n')
        code=run.wait()
    record=dict(status='COMPLETE' if code==0 else 'FAILED_OR_DEADLINE',returncode=code)
Path('logs/isolated_status.json').write_text(json.dumps(record,indent=2)+'\n')
print(record,flush=True)
