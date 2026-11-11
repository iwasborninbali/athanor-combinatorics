#!/usr/bin/env python3
"""Stdlib-only independent check of a two-certificate order-13 exclusion.

The prefix excludes all cliques whose minimum D4 representative is among its
K roots. The exact induced-subgraph reduction is checked from the permutations.
The second proof excludes a 12-clique in that remaining graph. No search module
or binary is imported. --filter-only checks ONLY the data relation, not proofs.
"""
import argparse,hashlib,json
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def load(path):
 lines=[tuple(map(int,line.split())) for line in Path(path).read_text().splitlines() if line.strip()]
 n,m=lines.pop(0);assert len(lines)==m
 assert len(set(lines))==m
 for a in lines:
  assert len(a)==n and sorted(a)==list(range(n))
  assert len({(j-i,a[j]-a[i]) for i in range(n) for j in range(i+1,n)})==n*(n-1)//2
 return n,lines
def filter_check(original,reduced,k):
 n,arrays=load(original);nn,subset=load(reduced);assert n==nn==13 and len(arrays)==12828
 lookup={a:i for i,a in enumerate(arrays)};reps=[]
 for a in arrays:
  images=[]
  for transpose in (False,True):
   for rr in (False,True):
    for cc in (False,True):
     image=[0]*n
     for r,c in enumerate(a):
      x,y=(c,r) if transpose else (r,c)
      if rr:x=n-1-x
      if cc:y=n-1-y
      image[x]=y
     images.append(lookup[tuple(image)])
  reps.append(min(images))
 roots=[i for i,r in enumerate(reps) if i==r];assert 0<k<len(roots);last=roots[k-1]
 expected=[a for a,r in zip(arrays,reps) if r>last];assert subset==expected,'reduced catalogue omits or adds eligible arrays'
 return {'verified':True,'scope':'exact induced-subgraph data relation only','original_roots':len(roots),'excluded_initial_roots':k,'last_excluded_representative_index':last,'remaining_roots':len(roots)-k,'remaining_vertices':len(subset),'original_catalogue_sha256':sha(original),'remaining_catalogue_sha256':sha(reduced)}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original');p.add_argument('prefix_proof');p.add_argument('roots',type=int);p.add_argument('reduced');p.add_argument('tail_proof');p.add_argument('--filter-only',action='store_true');a=p.parse_args()
 result=filter_check(a.original,a.reduced,a.roots)
 if not a.filter_only:
  from check_clique_prefix import verify as prefix_verify
  from check_clique_proof import verify as full_verify
  first=prefix_verify(a.original,a.prefix_proof,12,a.roots);second=full_verify(a.reduced,a.tail_proof,12)
  assert first['roots']==a.roots and second['roots']==result['remaining_roots']
  result.update(scope='complete exclusion of a 12-packing in the original catalogue',prefix_audit=first,remaining_graph_audit=second)
 print(json.dumps(result,indent=2))
