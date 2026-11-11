"""Reproduce exclusions sequentially, checking space before every write."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
CERT = ROOT / 'certificates'
LOGS = ROOT / 'logs'


def run():
    CERT.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    plan = [(2, [16]), (3, [28, 30, 32]), (4, list(range(48, 65, 2)))]
    summaries = []
    for k, orders in plan:
        subprocess.run(['python3', 'export_patterns.py', '--chords', str(k)], check=True, cwd=ROOT)
        for n in orders:
            assert shutil.disk_usage(ROOT).free >= 3*1024**3, 'less than 3 GiB free'
            stem = f'exclusion_k{k}_n{n}'
            raw_path = CERT / (stem+'.bpc')
            log_path = LOGS / (stem+'.jsonl')
            with raw_path.open('wb') as out, log_path.open('w') as err:
                p = subprocess.run([str(ROOT/'exhaustive'), f'patterns{k}.txt', str(n), '--proof'],
                                   cwd=ROOT, stdout=out, stderr=err)
            assert p.returncode == 0, (n, k, p.returncode, log_path.read_text()[-2000:])
            assert raw_path.stat().st_size < 512*1024**2
            zipped = raw_path.with_suffix('.bpc.gz')
            # No timestamps or paths in gzip metadata.
            with raw_path.open('rb') as src, zipped.open('wb') as dst:
                with gzip.GzipFile(filename='', fileobj=dst, mode='wb', mtime=0) as gz:
                    shutil.copyfileobj(src, gz)
            raw_size = raw_path.stat().st_size
            raw_path.unlink()
            summary = json.loads(log_path.read_text().splitlines()[-1])
            summary.update(proof=str(zipped.relative_to(ROOT)), compressed_bytes=zipped.stat().st_size,
                           uncompressed_bytes=raw_size)
            summaries.append(summary)
            print(json.dumps(summary), flush=True)
    (LOGS/'exclusion_summary.json').write_text(json.dumps(summaries, indent=2)+'\n')


if __name__ == '__main__':
    run()
