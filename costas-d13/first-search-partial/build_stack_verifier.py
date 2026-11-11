from pathlib import Path
s=Path('check_trace_parallel.cpp').read_text()
s=s.replace('#include <thread>','#include <thread>\n#include <pthread.h>\n#include <functional>\n#include <memory>')
needle='struct Segment {int first,last;uint64_t begin,end;};'
factory=r'''
// Explicit stacks comfortably cover all recursion depths for n<32.
struct WorkerPool {
 pthread_attr_t attributes;vector<pthread_t> workers;
 WorkerPool(){require(pthread_attr_init(&attributes)==0,"thread attribute init");require(pthread_attr_setstacksize(&attributes,8*1024*1024)==0,"thread stack allocation");}
 void emplace_back(function<void()> callback){
  auto* body=new function<void()>(std::move(callback));pthread_t worker;
  int status=pthread_create(&worker,&attributes,[](void* raw)->void*{unique_ptr<function<void()>> invoke(static_cast<function<void()>*>(raw));(*invoke)();return nullptr;},body);
  if(status){delete body;throw runtime_error("worker creation failed");}workers.push_back(worker);
 }
 void join(){for(auto worker:workers)pthread_join(worker,nullptr);workers.clear();}
 ~WorkerPool(){join();pthread_attr_destroy(&attributes);}
};
'''
s=s.replace(needle,factory+needle).replace('vector<thread> pool;','WorkerPool pool;').replace(' for(auto& worker:pool)worker.join();',' pool.join();')
s=s.replace('<<threads<<",\\\"segments', '<<threads<<",\\\"worker_stack_bytes\\\":8388608,\\\"segments')
Path('check_trace_parallel_stack.cpp').write_text('// Independent verifier with explicit per-worker stack limits.\n'+s)
