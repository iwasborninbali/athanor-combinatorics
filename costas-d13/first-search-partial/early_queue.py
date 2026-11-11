"""Continue the complete trace under the original wall/disk limits."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

deadline = datetime(2026, 11, 10, 23, 41, 31, tzinfo=timezone.utc)
Path('logs/early13.time-limit').write_text('7200\n')
shutil.copyfile('clique_early.cpp', 'logs/clique_early13.source.cpp')
shutil.copyfile('small_early.hpp', 'logs/clique_early13.small_early.hpp')
shutil.copyfile('clique_early', 'logs/clique_early13.executable')

def guarded(name, seconds, command):
    subprocess.run(['python3', 'run_guarded.py', '--name', name,
                    '--seconds', str(seconds), '--']+command, check=True)
    record = json.loads(Path(f'logs/{name}.guard.json').read_text())
    assert record['returncode'] == 0, record
    return record

guarded('clique_early13', 11000, ['./clique_early', 'data/costas_13.txt', '12',
    '7200', 'logs/clique_early13', 'resume', 'logs/clique_continue13.proof.gz',
    'logs/early13.time-limit'])
result = json.loads(Path('logs/clique_early13.json').read_text())
print(json.dumps(result), flush=True)
lower = Path('logs/clique_early13.lower.witness.json')
if lower.exists():
    witness = json.loads(lower.read_text())
    size = witness['size']
    destination = f'certificates/witness_13_{size}.json'
    shutil.copyfile(lower, destination)
    with open(f'logs/check_witness_13_{size}.json', 'w') as out:
        subprocess.run(['python3', 'check.py', destination, '--catalogue', 'data/costas_13.txt'], stdout=out, check=True)
if result['status'] == 'SAT':
    certificate = 'certificates/witness_13_12.json'
    shutil.copyfile('logs/clique_early13.witness.json', certificate)
    audit = 'logs/check_witness_13_12.json'
    with open(audit, 'w') as out:
        subprocess.run(['python3', 'check.py', certificate, '--catalogue', 'data/costas_13.txt'], stdout=out, check=True)
    record = {'kind': '12-packing', 'certificate': certificate, 'audit': audit}
    Path('logs/target_resolved.json').write_text(json.dumps(record, indent=2)+'\n')
    print('TARGET CERTIFICATE CHECKED: 12-packing', flush=True)
elif result['status'] == 'EXHAUSTED':
    certificate = 'certificates/no_12_clique.proof.gz'
    shutil.move('logs/clique_early13.proof.gz', certificate)
    seconds = int((deadline-datetime.now(timezone.utc)).total_seconds())-300
    assert seconds > 0
    guarded('cpp_check13_complete', seconds, ['python3', 'check_cpp_certificate.py', 'data/costas_13.txt', certificate, '12'])
    record = {'kind': 'no 12-packing', 'certificate': certificate,
              'audit': 'logs/cpp_check13_complete.stdout',
              'python_verifier': 'check_clique_proof.py'}
    Path('logs/target_resolved.json').write_text(json.dumps(record, indent=2)+'\n')
    print('TARGET CERTIFICATE CHECKED: no 12-packing', flush=True)
    # Also perform the full pure-Python check if the measured pilot rate,
    # with a safety factor, predicts that it fits the original wall budget.
    remaining = int((deadline-datetime.now(timezone.utc)).total_seconds())-300
    projected = result['nodes'] * (63.04/1678389) * 1.25
    if projected < remaining:
        guarded('python_check13_complete', remaining, ['python3', 'check_clique_proof.py', 'data/costas_13.txt', certificate, '12'])
        record['python_full_audit'] = 'logs/python_check13_complete.stdout'
    else:
        record['python_full_audit'] = 'not run: measured pilot projection exceeds remaining wall budget'
    Path('logs/target_resolved.json').write_text(json.dumps(record, indent=2)+'\n')
else:
    print('Continuation ended without a target certificate.', flush=True)
