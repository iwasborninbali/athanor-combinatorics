"""Small adversarial checks of the independent certificate validators."""
import contextlib
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from check_exclusions import verify

ROOT = Path(__file__).resolve().parent
results = []
original = gzip.decompress((ROOT/'certificates/exclusion_k2_n16.bpc.gz').read_bytes())
mutants = {
    'truncated': original[:-1],
    'trailing_data': original + b'\x02',
    'omitted_case': original[:6] + bytes([original[6]-1, original[7]]) + original[8:],
    # Skip branch bytes until the first prune. Asserting that the Hamilton
    # half-length is absent must fail: the Hamilton cycle is always present.
}
bad = bytearray(original)
i = 10
while bad[i] == 0:
    i += 1
bad[i] = 8
mutants['unsound_Hamilton_leaf'] = bytes(bad)
with tempfile.TemporaryDirectory(prefix='checker-rejection-',dir=ROOT) as tmp:
    tmp = Path(tmp)
    for name,data in mutants.items():
        p = tmp/(name+'.bpc')
        p.write_bytes(data)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                verify(p)
        except AssertionError as exc:
            results.append({'case':name,'verdict':'REJECTED','reason':str(exc)})
        else:
            raise AssertionError(('bad proof accepted',name))
    bad_witness = [{'N':46,'chords':[[0,5],[0,43],[1,38]]}]
    p = tmp/'bad_witness.json'
    p.write_text(json.dumps(bad_witness))
    call = subprocess.run([sys.executable,str(ROOT/'check_witnesses.py'),str(p)],capture_output=True,text=True)
    assert call.returncode != 0 and 'AssertionError' in call.stderr
    results.append({'case':'missing_chord_from_46','verdict':'REJECTED'})
(ROOT/'logs/checker_rejection.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
