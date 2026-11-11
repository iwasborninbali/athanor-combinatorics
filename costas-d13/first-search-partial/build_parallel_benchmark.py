from pathlib import Path
s=Path('check_prefix_parallel.cpp').read_text()
s=s.replace('struct Trace {','struct SampleStop {};\nstruct Trace {')
s=s.replace('nodes++;','nodes++;if(nodes>1000000)throw SampleStop{};')
s=s.replace('original.segment(last_offset,~uint64_t(0));while(original.next()>=0){}', '(void)last_offset;')
s=s.replace('vector<thread> pool;','vector<thread> pool;atomic<int> positioned{0};vector<double> sample_seconds(threads);')
s=s.replace('pool.emplace_back([&]{try{','pool.emplace_back([&,worker]{try{')
a=s.index('  while(!failed){');b=s.index('\n }catch(const exception& problem)',a)
s=s[:a]+'''  int index=next.fetch_add(1);require(index<(int)segments.size(),"too few benchmark ranges");auto job=segments[index];stream.segment(job.begin,job.end);
  positioned.fetch_add(1);while(positioned.load()<threads && !failed.load())this_thread::yield();require(!failed.load(),"benchmark setup failed");
  auto sample_start=chrono::steady_clock::now();
  try{audit.run_range(job.first,job.last,false);throw runtime_error("benchmark range completed before the sample limit");}
  catch(const SampleStop&){counts[index]=1000000;sample_seconds[worker]=chrono::duration<double>(chrono::steady_clock::now()-sample_start).count();}
'''+s[b:]
s=s.replace('require(roots==(uint64_t)root_limit,"incomplete aggregate scoped coverage");','')
a=s.index(' cout<<"{\\\"verified\\\":true');b=s.index('\n return 0;',a)
s=s[:a]+r''' cout<<"{\"complete\":false,\"purpose\":\"performance sample only; NOT a certificate check\",\"sample_nodes\":"<<nodes<<",\"threads\":"<<threads<<",\"wall_seconds_including_seek\":"<<seconds<<",\"verification_seconds_by_thread\":[";for(int i=0;i<threads;i++)cout<<(i?",":"")<<sample_seconds[i];cout<<"]}\n";'''+s[b:]
Path('benchmark_parallel13.cpp').write_text('// PERFORMANCE ONLY: deliberate early stop, not a proof verifier.\n'+s)
