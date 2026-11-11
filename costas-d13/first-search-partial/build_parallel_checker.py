from pathlib import Path
s=Path('check_trace.cpp').read_text()
s=s.replace('#include <algorithm>','#include <algorithm>\n#include <atomic>\n#include <mutex>\n#include <thread>')
s=s.replace('struct Trace {','std::atomic<uint64_t> progress_nodes{0};\nstd::mutex log_mutex;\nstruct Trace {')
s=s.replace('int pos=0,length=0;','int pos=0,length=0;uint64_t cursor=0,stop=~uint64_t(0);')
s=s.replace(' int next(){\n  if(pos==length)', ' void segment(uint64_t begin,uint64_t end){require(begin<=end,"reversed trace range");require(gzseek(f,(z_off_t)begin,SEEK_SET)==(z_off_t)begin,"trace seek failure");pos=length=0;cursor=begin;stop=end;}\n int next(){\n  if(cursor==stop)return -1;\n  if(pos==length)')
s=s.replace('length=gzread(f,buffer,sizeof(buffer));','length=gzread(f,buffer,min<uint64_t>(sizeof(buffer),stop-cursor));')
s=s.replace('  return buffer[pos++];','  cursor++;return buffer[pos++];')
needle=' bool edge(int u,int v)const'
copy=''' Audit(const Audit& source,Trace& input):n(source.n),m(source.m),target(source.target),words(source.words),arrays(source.arrays),inverse(source.inverse),neighbors(source.neighbors),representative(source.representative),trace(input){start=chrono::steady_clock::now();}
'''
assert needle in s;s=s.replace(needle,copy+needle)
s=s.replace('if(nodes%1048576==0)cerr<<"verified_nodes="<<nodes<<" seconds="<<seconds()<<"\\n";', 'if(nodes%1048576==0){auto total=progress_nodes.fetch_add(1048576)+1048576;lock_guard<mutex> hold(log_mutex);cerr<<"verified_nodes_approx="<<total<<"\\n";}')
a=s.index(' void run(){');b=s.index('\n};\nint main',a)
s=s[:a]+''' void run_range(int begin,int end){
  require(begin>=0&&end>begin,"invalid root range");int ordinal=0;uint64_t before=roots;
  for(int i=0;i<m;i++)if(representative[i]==i){
   int current=ordinal++;if(current<begin)continue;if(current>=end)break;
   vector<int> candidates;for(int j=i+1;j<m;j++)if(representative[j]>=i&&edge(i,j))candidates.push_back(j);
   selection={i};node(candidates,target-1);roots++;
  }
  require(roots-before==(uint64_t)(end-begin),"root range not covered");
  require(trace.next()<0,"unconsumed bytes in certified root range");
 }
'''+s[b:]
s=s[:s.index('\nint main')]+r'''
struct Segment {int first,last;uint64_t begin,end;};
int main(int argc,char**argv){try{
 require(argc==6,"usage: check_trace_parallel catalogue trace.gz target boundaries.txt threads");
 int threads=stoi(argv[5]);require(threads>0&&threads<=3,"thread count must be 1..3");
 auto started=chrono::steady_clock::now();Trace original(argv[2]);Audit base(argv[1],stoi(argv[3]),original);
 int total_roots=0;for(int i=0;i<base.m;i++)if(base.representative[i]==i)total_roots++;
 ifstream metadata(argv[4]);require(bool(metadata),"cannot open boundaries");
 vector<Segment> segments;int root=0,last_root=0;uint64_t offset=0,last_offset=0;
 while(metadata>>root>>offset){require(root>last_root&&root<=total_roots&&offset>last_offset&&offset<10000000000ULL,"invalid boundary");segments.push_back({last_root,root,last_offset,offset});last_root=root;last_offset=offset;}
 require(metadata.eof()&&!segments.empty()&&last_root==total_roots,"boundary ranges do not cover all canonical roots");
 // Read through the complete gzip stream: all members, footer CRCs, the
 // final completion marker, and EOF are checked independently of ranges.
 original.segment(last_offset,~uint64_t(0));for(char c:string("ENDPROOF"))require(original.byte()==c,"missing completion marker");require(original.next()<0,"trailing proof data");
 vector<uint64_t> counts(segments.size()),root_counts(segments.size());atomic<int> next{0};atomic<bool> failed{false};string error;
 vector<thread> pool;
 for(int worker=0;worker<threads;worker++)pool.emplace_back([&]{try{
  Trace stream(argv[2]);Audit audit(base,stream);
  while(!failed){int index=next.fetch_add(1);if(index>=(int)segments.size())break;auto job=segments[index];stream.segment(job.begin,job.end);uint64_t before=audit.nodes,before_roots=audit.roots;audit.run_range(job.first,job.last);counts[index]=audit.nodes-before;root_counts[index]=audit.roots-before_roots;}
 }catch(const exception& problem){failed=true;lock_guard<mutex> hold(log_mutex);error=problem.what();}});
 for(auto& worker:pool)worker.join();require(!failed,error.c_str());uint64_t nodes=0,roots=0;for(auto value:counts)nodes+=value;for(auto value:root_counts)roots+=value;require(roots==(uint64_t)total_roots,"incomplete aggregate root coverage");
 double seconds=chrono::duration<double>(chrono::steady_clock::now()-started).count();
 cout<<"{\"verified\":true,\"order\":"<<base.n<<",\"excluded_clique_size\":"<<base.target<<",\"nodes\":"<<nodes<<",\"roots\":"<<roots<<",\"seconds\":"<<seconds<<",\"threads\":"<<threads<<",\"segments\":"<<segments.size()<<"}\n";
 return 0;
}catch(const exception& problem){cerr<<"REJECTED: "<<problem.what()<<"\n";return 1;}}
'''
Path('check_trace_parallel.cpp').write_text('// Independent full verifier; root ranges are verified, never trusted.\n'+s)
