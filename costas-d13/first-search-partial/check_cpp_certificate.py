#!/usr/bin/env python3
"""Stdlib driver for separate C++ proof verifiers.

The standalone pure-Python implementation is check_clique_proof.py.
--boundaries selects the parallel checker. For the completed primary target,
its recorded root offsets are materialized as a small certificate input and
passed to that checker automatically; the checker does not trust their scope
or alignment and independently enforces complete coverage and stream validity.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('catalogue');ap.add_argument('proof');ap.add_argument('target',type=int)
ap.add_argument('--boundaries');ap.add_argument('--threads',type=int,default=3)
args=ap.parse_args()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
if not args.boundaries and Path(args.proof).name=='no_12_clique.proof.gz' and args.target==12:
 result=json.loads(Path('logs/clique_early13.json').read_text())
 assert result['status']=='EXHAUSTED' and result['order']==13
 pairs=[(int(root),int(offset)) for root,offset in re.findall(r'roots=(\d+).*?nodes=(\d+)',Path('logs/clique_early13.stderr').read_text())]
 if not pairs or pairs[-1]!=(result['roots'],result['nodes']):pairs.append((result['roots'],result['nodes']))
 path=Path('certificates/no_12_clique.boundaries.txt')
 path.write_text(''.join(f'{root} {offset}\n' for root,offset in pairs))
 args.boundaries=str(path)
if args.boundaries:
 command=['./check_trace_parallel_stack',args.catalogue,args.proof,str(args.target),args.boundaries,str(args.threads)]
 code='check_trace_parallel_stack.cpp';binary='check_trace_parallel_stack'
else:
 command=['./check_trace',args.catalogue,args.proof,str(args.target)]
 code='check_trace.cpp';binary='check_trace'
before={'catalogue':sha(args.catalogue),'proof':sha(args.proof),'source':sha(code),'binary':sha(binary)}
if args.boundaries:before['boundaries']=sha(args.boundaries)
run=subprocess.run(command,stdout=subprocess.PIPE,text=True,check=True)
record=json.loads(run.stdout);assert record['verified'] and record['excluded_clique_size']==args.target
assert sha(args.catalogue)==before['catalogue'] and sha(args.proof)==before['proof']
record.update(catalogue_sha256=before['catalogue'],proof_sha256=before['proof'],verifier_source_sha256=before['source'],verifier_binary_sha256=before['binary'],verifier_source=code,backend='parallel root ranges' if args.boundaries else 'serial')
if args.boundaries:
 assert sha(args.boundaries)==before['boundaries']
 record.update(boundaries_file=args.boundaries,boundaries_sha256=sha(args.boundaries))
print(json.dumps(record,indent=2))
