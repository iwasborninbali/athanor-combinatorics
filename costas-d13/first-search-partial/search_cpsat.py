"""One-thread catalogue set packing; discovery tool, not a proof checker."""
import argparse
import hashlib
import json
import pathlib
import time

from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('order', type=int)
    ap.add_argument('target', type=int)
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--log', action='store_true')
    ap.add_argument('--holes', action='store_true', help='explicit complement permutation (target n-1)')
    ap.add_argument('--linearization', type=int, default=1)
    args = ap.parse_args()
    path = pathlib.Path(f'data/costas_{args.order}.txt')
    words = list(map(int, path.read_text().split()))
    n, count = words[:2]
    assert n == args.order and len(words) == 2 + n * count
    arrays = [words[2+i*n:2+(i+1)*n] for i in range(count)]
    model = cp_model.CpModel()
    selected = [model.new_bool_var(f'a{i}') for i in range(count)]
    cells = [[] for _ in range(n*n)]
    for a, var in zip(arrays, selected):
        for row, col in enumerate(a):
            cells[row*n+col].append(var)
    if args.holes:
        assert args.target == n - 1
        holes = [model.new_bool_var(f'h{i}') for i in range(n*n)]
        for i, group in enumerate(cells):
            model.add_exactly_one(group + [holes[i]])
        for r in range(n):
            model.add_exactly_one(holes[r*n:(r+1)*n])
        for c in range(n):
            model.add_exactly_one([holes[r*n+c] for r in range(n)])
    else:
        for group in cells:
            model.add_at_most_one(group)
    model.add(sum(selected) == args.target)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.random_seed = args.seed
    solver.parameters.log_search_progress = args.log
    solver.parameters.linearization_level = args.linearization
    start = time.monotonic()
    status = solver.solve(model)
    elapsed = time.monotonic() - start
    record = {'order': n, 'target': args.target, 'seed': args.seed,
              'status': solver.status_name(status), 'elapsed_seconds': elapsed,
              'catalogue_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'stats': solver.response_stats(), 'workers': 1,
              'holes': args.holes, 'linearization': args.linearization}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        ids = [i for i, v in enumerate(selected) if solver.boolean_value(v)]
        witness = {'order': n, 'size': len(ids), 'index_base': 0,
                   'catalogue_row_indices': ids, 'arrays': [arrays[i] for i in ids]}
        wp = pathlib.Path(f'certificates/witness_{n}_{len(ids)}.json')
        wp.write_text(json.dumps(witness, indent=2) + '\n')
        record['witness'] = str(wp)
    suffix = f'_holes_lp{args.linearization}' if args.holes else ''
    out = pathlib.Path(f'logs/cpsat_{n}_{args.target}_seed{args.seed}{suffix}.json')
    out.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
