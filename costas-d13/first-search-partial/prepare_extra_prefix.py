from pathlib import Path
s=Path('check_prefix_parallel.cpp').read_text();full=Path('check_trace_parallel_stack.cpp').read_text();factory=full[full.index('// Explicit stacks'):full.index('struct Segment')]
s=s.replace('#include <thread>','#include <thread>\n#include <pthread.h>\n#include <functional>\n#include <memory>')
s=s.replace('struct Segment {int first,last;uint64_t begin,end;};',factory+'struct Segment {int first,last;uint64_t begin,end;};')
s=s.replace('vector<thread> pool;','WorkerPool pool;').replace(' for(auto& worker:pool)worker.join();',' pool.join();')
Path('check_prefix_parallel_stack.cpp').write_text('// Explicit-stack restricted-root verifier; no global bound by itself.\n'+s)
