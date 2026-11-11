#!/usr/bin/env python3
"""Stop only this workspace's detached groups before the six-hour deadline."""
import datetime
import json
import os
import signal
import time
from pathlib import Path

end = datetime.datetime(2026, 11, 11, 3, 8, tzinfo=datetime.timezone.utc).timestamp()
groups = {int(k):v for k,v in json.loads(Path('logs/active_groups.json').read_text()).items()}

while time.time() < end:
    p = Path('certificates/order13_manifest.json')
    if p.exists():
        try:
            if json.loads(p.read_text())['status'] == 'EXHAUSTED_INDEPENDENTLY_VERIFIED' and Path('logs/isolated_status.json').exists():
                print('All proof verification completed before the deadline.', flush=True)
                raise SystemExit(0)
        except (OSError, ValueError, KeyError):
            pass
    time.sleep(min(60, max(1, end - time.time())))
stopped = []
for pid, name in groups.items():
    try:
        command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
        if name not in command or os.getpgid(pid) != pid:
            continue
        os.killpg(pid, signal.SIGTERM)
        stopped.append(dict(pgid=pid, command=command))
    except (FileNotFoundError, ProcessLookupError):
        pass
Path('logs/deadline_stop.json').write_text(json.dumps(stopped, indent=2) + '\n')
print('Deadline reached; stopped only matching research process groups.', stopped, flush=True)
