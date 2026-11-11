"""Pilot and witness search with OR-Tools CP-SAT; not an UNSAT certificate."""
import argparse
import json
import time
from pathlib import Path
from ortools.sat.python import cp_model
from patterns import build


def solve(n, k, seconds, out):
    start = time.monotonic()
    for p in build(k):
        if len(p['cycles']) < n//2-1:
            continue
        model = cp_model.CpModel()
        a = [model.new_int_var(0, n, f'a{i}') for i in range(2*k)]
        model.add(sum(a) == n)
        for u, v in p['pairs']:
            h = model.new_int_var(1, n//2-2, f'h{u}_{v}')
            model.add(sum(a[u:v]) == 2*h+1)
        exprs = [sum(a[j] for j in c['arcs']) + c['chords'] for c in p['cycles']]
        for t in range(4, n, 2):
            bs = []
            for j, expr in enumerate(exprs):
                if p['cycles'][j]['chords'] == 0:
                    continue
                b = model.new_bool_var(f'c{j}_t{t}')
                model.add(expr == t).only_enforce_if(b)
                # Contracting unused zero arcs must never identify two
                # separate pieces of a cycle. Every maximal unused circular
                # arc run has cycle vertices at its ends, so its total length
                # must be positive if this cycle is used.
                used = set(p['cycles'][j]['arcs'])
                m = 2*k
                for z in range(m):
                    if z not in used and (z-1) % m in used:
                        gap = []
                        i = z
                        while i not in used:
                            gap.append(i)
                            i = (i+1) % m
                        model.add(sum(a[i] for i in gap) >= 1).only_enforce_if(b)
                bs.append(b)
            model.add_bool_or(bs)
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.max_time_in_seconds = seconds
        solver.parameters.random_seed = 20261111
        before = time.monotonic()
        status = solver.solve(model)
        record = {'N': n, 'k': k, 'pattern': p['id'], 'status': solver.status_name(status),
                  'seconds': time.monotonic()-before, 'branches': solver.num_branches,
                  'conflicts': solver.num_conflicts}
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            arcs = [solver.value(x) for x in a]
            pos = [sum(arcs[:j]) for j in range(2*k)]
            chords = sorted([sorted([pos[u] % n, pos[v] % n]) for u, v in p['pairs']])
            record.update(arcs=arcs, chords=chords)
        with open(out, 'a') as f:
            f.write(json.dumps(record) + '\n')
        print(json.dumps(record), flush=True)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return record
    print(json.dumps({'N': n, 'k': k, 'total_seconds': time.monotonic()-start}), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('N', type=int, nargs='+')
    ap.add_argument('--chords', type=int, default=4)
    ap.add_argument('--seconds', type=float, default=30)
    ap.add_argument('--out', default='cp_pilot.jsonl')
    args = ap.parse_args()
    for n in args.N:
        solve(n, args.chords, args.seconds, args.out)
