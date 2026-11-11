"""Adversarial smoke checks for the independent certificate checkers."""
import copy
import gzip
import json
from pathlib import Path
import tempfile

from check import check
from check_clique_proof import verify
from check_sat_encoding import verify_encoding

results = []

def rejected(name, function):
    try:
        function()
    except (AssertionError, EOFError, gzip.BadGzipFile):
        results.append({'case': name, 'rejected': True})
    else:
        raise AssertionError(('invalid input accepted', name))

with tempfile.TemporaryDirectory(dir='.', prefix='checker-audit-') as directory:
    directory = Path(directory)
    witness = json.loads(Path('certificates/witness_10_10.json').read_text())
    bad = copy.deepcopy(witness)
    bad['arrays'][1] = bad['arrays'][0][:]
    p = directory/'duplicate.json'
    p.write_text(json.dumps(bad))
    rejected('two arrays share cells', lambda: check(p))
    bad = copy.deepcopy(witness)
    bad['arrays'][0] = list(range(10))
    p = directory/'not-costas.json'
    p.write_text(json.dumps(bad))
    rejected('permutation has repeated displacement', lambda: check(p))
    raw = gzip.decompress(Path('logs/clique_5_5.proof.gz').read_bytes())
    p = directory/'truncated.gz'
    p.write_bytes(gzip.compress(raw[:-8]))
    rejected('missing exclusion completion marker', lambda: verify('data/costas_5.txt', p, 5))
    p = directory/'opcode.gz'
    p.write_bytes(gzip.compress(bytes([255])+raw[1:]))
    rejected('invalid exclusion opcode', lambda: verify('data/costas_5.txt', p, 5))
    p = directory/'wrong.cnf'
    lines = Path('data/full_5_sym.cnf').read_text().splitlines()
    lines[-1] = '1 0'
    p.write_text('\n'.join(lines)+'\n')
    rejected('changed CNF clause', lambda: verify_encoding('data/costas_5.txt', p, True, True))
Path('logs/checker_adversarial_audit.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results))
