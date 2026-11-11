"""Sequential bounded trials; exactly one heavy computation at a time."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

DEADLINE = datetime(2026, 11, 10, 23, 41, 31, tzinfo=timezone.utc)


def guard(name, seconds, command):
    subprocess.run(['python3', 'run_guarded.py', '--name', name,
                    '--seconds', str(seconds), '--']+command, check=True)
    return json.loads(Path(f'logs/{name}.guard.json').read_text())


def discard_incomplete(path):
    path = Path(path)
    if not path.exists():
        return
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    record = {'path': str(path), 'bytes': path.stat().st_size,
              'sha256': h.hexdigest(), 'disposition': 'deleted: incomplete, no exclusion certificate'}
    path.with_suffix(path.suffix+'.deleted.json').write_text(json.dumps(record, indent=2)+'\n')
    path.unlink()


def solved(kind, certificate, audit):
    Path('logs/target_resolved.json').write_text(json.dumps(
        {'kind': kind, 'certificate': certificate, 'audit': audit}, indent=2)+'\n')
    print('TARGET CERTIFICATE CHECKED: '+kind, flush=True)


assert shutil.disk_usage('.').free >= 3*1024**3
r = guard('pairwise_gen13', 180, ['./make_pairwise_cnf', 'data/costas_13.txt', 'data/holes_13_direct.cnf.gz'])
assert r['returncode'] == 0
r = guard('pairwise_encoding13', 300, ['python3', 'check_pairwise_cnf.py', 'data/costas_13.txt', 'data/holes_13_direct.cnf.gz'])
assert r['returncode'] == 0
proof = 'logs/holes_13_direct_trial.drat.gz'
r = guard('kissat_direct13', 210, ['/opt/homebrew/bin/kissat', '--time=180', '--sat',
    '--preprocess=false', '--eliminate=false', '--factor=false', '--congruence=false',
    '--sweep=false', '--probe=false', '--vivify=false', 'data/holes_13_direct.cnf.gz', proof])
assert r['returncode'] in (0, 10, 20)
if r['returncode'] == 10:
    witness = 'certificates/witness_13_12.json'
    subprocess.run(['python3', 'extract_sat.py', 'data/costas_13.txt', 'logs/kissat_direct13.stdout', witness], check=True)
    with open('logs/check_witness_13_12.json', 'w') as out:
        subprocess.run(['python3', 'check.py', witness, '--catalogue', 'data/costas_13.txt'], stdout=out, check=True)
    solved('12-packing', witness, 'logs/check_witness_13_12.json')
elif r['returncode'] == 20:
    proof_copy = 'certificates/no_12_direct.drat.gz'
    shutil.move(proof, proof_copy)
    r = guard('direct_unsat_check13', 3600, ['python3', 'check_pairwise_cnf.py', 'data/costas_13.txt', 'data/holes_13_direct.cnf.gz', '--proof', proof_copy, '--seconds', '3500', '--proof-log', 'logs/drat_no12_direct.log'])
    assert r['returncode'] == 0
    solved('no 12-packing', proof_copy, 'logs/direct_unsat_check13.stdout')
else:
    discard_incomplete(proof)
    r = guard('clique_long13', 1530, ['./clique_nomatch', 'data/costas_13.txt', '12', '1500', 'logs/clique_long13', 'proof'])
    assert r['returncode'] == 0
    result = json.loads(Path('logs/clique_long13.json').read_text())
    print(json.dumps(result), flush=True)
    if result['status'] == 'SAT':
        witness = 'certificates/witness_13_12.json'
        shutil.copyfile('logs/clique_long13.witness.json', witness)
        with open('logs/check_witness_13_12.json', 'w') as out:
            subprocess.run(['python3', 'check.py', witness, '--catalogue', 'data/costas_13.txt'], stdout=out, check=True)
        solved('12-packing', witness, 'logs/check_witness_13_12.json')
    elif result['status'] == 'EXHAUSTED':
        proof_copy = 'certificates/no_12_clique.proof.gz'
        shutil.copyfile('logs/clique_long13.proof.gz', proof_copy)
        seconds = int((DEADLINE-datetime.now(timezone.utc)).total_seconds())-300
        assert seconds > 0
        r = guard('clique_unsat_check13', seconds, ['python3', 'check_clique_proof.py', 'data/costas_13.txt', proof_copy, '12'])
        assert r['returncode'] == 0
        solved('no 12-packing', proof_copy, 'logs/clique_unsat_check13.stdout')
    else:
        print('Target remains open after these trials.', flush=True)
