#!/usr/bin/env python3
"""Balance only this run's two existing decoders across the allowed cores."""
import datetime
import json
import os
import re
import time
from pathlib import Path

jobs = [('even',1060060,1113548025),('odd',1060063,1135562948)]
with open('logs/audit_balancing.jsonl','a') as log:
    while True:
        active=[]
        for name,pid,total in jobs:
            try:
                command=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
                if not command.startswith('checkers/check_roots data/costas_13.txt /dev/stdin 12 2 ') or os.getpgid(pid)!=1005339:
                    continue
                text=Path(f'logs/check13_{name}.stderr').read_text()
                matches=re.findall(r'verified_nodes=(\d+)',text)
                done=int(matches[-1]) if matches else 0
                active.append((max(0,total-done),name,pid))
            except (FileNotFoundError,ProcessLookupError):
                pass
        if not active:
            break
        active.sort(reverse=True)
        for rank,(remaining,name,pid) in enumerate(active):
            # CPU 3 had no direct co-tenant; CPU 2 had two external scan jobs.
            wanted={3 if rank==0 else 2}
            try:
                old=os.sched_getaffinity(pid)
                if old!=wanted:
                    os.sched_setaffinity(pid,wanted)
                    event=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=pid,scope=name,
                               remaining_states_estimate=remaining,old_affinity=sorted(old),new_affinity=sorted(wanted))
                    log.write(json.dumps(event)+'\n');log.flush()
            except ProcessLookupError:
                pass
        time.sleep(20)
print('Both decoder processes exited; balancing complete.',flush=True)
