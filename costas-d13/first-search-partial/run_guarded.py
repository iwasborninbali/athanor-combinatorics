"""Run one computation with time/disk/folder guards and an hourly progress log."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def stamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('command', nargs=argparse.REMAINDER)
    args = ap.parse_args()
    command = args.command
    if command[:1] == ['--']:
        command = command[1:]
    started = time.monotonic()
    prefix = Path('logs') / args.name
    record = {'started_utc': stamp(), 'command': command, 'original_wall_limit_seconds': args.seconds}
    record['code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(Path('.').glob('*'))
                             if p.is_file() and p.suffix in ('.py', '.cpp')}
    executable = Path(command[0])
    if executable.is_file():
        record['executable_sha256'] = hashlib.sha256(executable.read_bytes()).hexdigest()
    def note(message):
        with open('progress.md', 'a') as f:
            f.write(f'\n- {stamp()}: {args.name}: {message}\n')
    note('started; one heavy process')
    reason = 'finished'
    with open(str(prefix)+'.stdout', 'w') as out, open(str(prefix)+'.stderr', 'w') as err:
        process = subprocess.Popen(command, stdout=out, stderr=err, start_new_session=True)
        record['pid'] = process.pid
        last_note = started
        while process.poll() is None:
            now = time.monotonic()
            time_limit_reached = now-started > args.seconds
            deadline_file = Path(str(prefix)+'.deadline')
            if deadline_file.exists():
                try:
                    chosen = datetime.fromisoformat(deadline_file.read_text().strip())
                    ceiling = datetime(2026,11,10,23,40,0,tzinfo=timezone.utc)
                    if chosen.tzinfo is not None:
                        chosen = min(chosen.astimezone(timezone.utc), ceiling)
                        if record.get('deadline_override_utc') != chosen.isoformat():
                            record['deadline_override_utc'] = chosen.isoformat()
                            note('absolute deadline adjusted within original six-hour budget: '+chosen.isoformat())
                        time_limit_reached = datetime.now(timezone.utc) >= chosen
                except (ValueError, OSError):
                    pass
            used = sum(p.stat().st_size for p in Path('.').rglob('*') if p.is_file())
            free = shutil.disk_usage('.').free
            if free < 3*1024**3:
                reason = 'free_disk_below_3GiB'
            elif used > 950*1024**2:
                reason = 'folder_above_950MiB'
            elif time_limit_reached:
                reason = 'wall_time_limit'
            else:
                memory = subprocess.run(['ps', '-o', 'rss=', '-p', str(process.pid)], capture_output=True, text=True)
                if memory.stdout.strip() and int(memory.stdout.strip()) > 6*1024*1024:
                    reason = 'process_rss_above_6GiB'
            if reason != 'finished':
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                break
            if now-last_note >= 1800:
                note(f'running for {now-started:.0f}s; folder {used/1024**2:.1f} MiB; free disk {free/1024**3:.1f} GiB')
                last_note = now
            time.sleep(2)
        record.update(returncode=process.wait(), stop_reason=reason,
                      elapsed_seconds=time.monotonic()-started, ended_utc=stamp())
    Path(str(prefix)+'.guard.json').write_text(json.dumps(record, indent=2)+'\n')
    note(f'ended: {reason}; return code {record["returncode"]}; elapsed {record["elapsed_seconds"]:.1f}s')
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
