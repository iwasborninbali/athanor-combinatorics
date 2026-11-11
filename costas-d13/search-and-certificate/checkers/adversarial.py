#!/usr/bin/env python3
"""Check that semantic damage cannot masquerade as a complete exclusion."""
import gzip
import json
import subprocess
from pathlib import Path

source = Path('certificates/new_9_9.proof.gz')
payload = gzip.decompress(source.read_bytes())
assert payload.endswith(b'ENDPROOF')
variants = {
    'missing_marker': payload[:-8],
    'missing_node': payload[:-9] + payload[-8:],
    'unknown_opcode': bytes([255]) + payload[1:],
    'false_cardinality': bytes([253]) + payload[1:],
    'trailing_stream': payload + b'X',
}
results = []
for name, content in variants.items():
    path = Path(f'logs/bad_{name}.proof.gz')
    path.write_bytes(gzip.compress(content, mtime=0))
    for checker in ['cpp', 'own_python', 'copied_python']:
        if checker == 'cpp':
            command = ['checkers/check_trace']
        elif checker == 'own_python':
            command = ['python3', 'checkers/audit_speed.py']
        else:
            command = ['python3', 'checkers/check_clique_proof.py']
        command += ['data/costas_9.txt', str(path), '9']
        run = subprocess.run(command, capture_output=True, text=True)
        results.append(dict(damage=name, checker=checker, rejected=run.returncode != 0,
                            returncode=run.returncode, error=run.stderr[-1000:]))
        assert run.returncode != 0, (name, checker, run.stdout)
# Raw transport damage must also be rejected, even if advice bytes survived.
raw = source.read_bytes()
for name, content in {'raw_truncated': raw[:-5], 'bad_crc': raw[:-8] + bytes([raw[-8] ^ 1]) + raw[-7:]}.items():
    path = Path(f'logs/bad_{name}.proof.gz')
    path.write_bytes(content)
    for checker, command in [('cpp', ['checkers/check_trace']), ('own_python', ['python3','checkers/audit_speed.py']), ('copied_python', ['python3','checkers/check_clique_proof.py'])]:
        run = subprocess.run(command + ['data/costas_9.txt', str(path), '9'], capture_output=True, text=True)
        results.append(dict(damage=name,checker=checker,rejected=run.returncode!=0,returncode=run.returncode,error=run.stderr[-1000:]))
        assert run.returncode != 0, (name, checker)
Path('logs/adversarial_checks.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(dict(all_rejected=True, cases=len(results))))
