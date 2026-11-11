from pathlib import Path
for name in ('check_trace_parallel.cpp','check_prefix_parallel.cpp'):
 p=Path(name);s=p.read_text()
 s=s.replace('vector<vector<uint64_t>> neighbors;vector<int>', 'vector<vector<uint64_t>> neighbors;const vector<vector<uint64_t>>* neighbor_view=nullptr;vector<int>')
 s=s.replace('  start=chrono::steady_clock::now();\n }','  neighbor_view=&neighbors;start=chrono::steady_clock::now();\n }',1)
 s=s.replace('neighbors(source.neighbors),representative', 'neighbor_view(source.neighbor_view),representative')
 s=s.replace('return (neighbors[u][v/64]>>(v%64))&1;', 'return ((*neighbor_view)[u][v/64]>>(v%64))&1;')
 assert 'neighbors(source.neighbors)' not in s and 'neighbor_view=&neighbors' in s
 p.write_text(s)
