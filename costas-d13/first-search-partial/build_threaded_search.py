from pathlib import Path
s=Path('clique_early.cpp').read_text();s=s[:s.index('int main(int argc')]
s=s.replace('#include <algorithm>','#include <algorithm>\n#include <atomic>\n#include <thread>\n#include <mutex>\n#include <filesystem>')
s=s.replace('vector<int> rep,path,answer;','vector<int> rep;\nthread_local vector<int> path,answer;')
for old,new in [
 ('uint64_t nodes=0;','thread_local uint64_t nodes=0;'),
 ('uint64_t matching_checks=0,matching_cuts=0;','thread_local uint64_t matching_checks=0,matching_cuts=0;'),
 ('uint64_t repair_attempts=0,repair_used=0,repair_closed=0;','thread_local uint64_t repair_attempts=0,repair_used=0,repair_closed=0;'),
 ('string output_prefix;','thread_local string output_prefix;'),('int best_lower=0;','thread_local int best_lower=0;'),
 ('bool timeout=false;','thread_local bool timeout=false;'),('string stop_reason;','thread_local string stop_reason;'),
 ('double slice_seconds=0,root_started=0;','thread_local double slice_seconds=0,root_started=0;'),
 ('bool root_cut=false;','thread_local bool root_cut=false;'),('gzFile proof=nullptr;','thread_local gzFile proof=nullptr;'),
 ('gzFile replay_input=nullptr;','thread_local gzFile replay_input=nullptr;'),('bool replaying=false;','thread_local bool replaying=false;'),
 ('uint64_t replayed_nodes=0;','thread_local uint64_t replayed_nodes=0;'),('string replay_path;','thread_local string replay_path;'),('string time_control;','thread_local string time_control;'),
 ('chrono::steady_clock::time_point started;','thread_local chrono::steady_clock::time_point started;')]:
 assert old in s,old;s=s.replace(old,new,1)
s=s.replace('using Bits=vector<uint64_t>;','using Bits=vector<uint64_t>;\natomic<bool> search_stop{false};')
s=s.replace('bool enter_node(){\n ++nodes;','bool enter_node(){\n if(search_stop.load(memory_order_relaxed)){timeout=true;stop_reason="peer_stop";return false;}\n ++nodes;')
s+=r'''
struct RootJob {bool done=false;uint64_t nodes=0;string file;};
int main(int argc,char**argv){
 if(argc!=6){cerr<<"usage: clique_threaded catalogue target seconds output-prefix threads\n";return 2;}
 target=stoi(argv[2]);limitsec=stod(argv[3]);string prefix=argv[4];int workers=stoi(argv[5]);if(workers<1||workers>3)return 2;
 ifstream input(argv[1]);input>>n>>m;if(n<1||n>31||m<1)return 2;
 a.assign(m,vector<int>(n));for(auto& row:a)for(int& value:row)input>>value;if(!input)return 2;
 partition_keys.assign(m,vector<int>(2*n));for(int i=0;i<m;i++)for(int r=0;r<n;r++){partition_keys[i][r]=a[i][r];partition_keys[i][n+a[i][r]]=r;}
 W=(m+63)/64;adj.assign(m,Bits(W));rep.resize(m);map<vector<int>,int> lookup;for(int i=0;i<m;i++)lookup[a[i]]=i;
 for(int i=0;i<m;i++){rep[i]=i;for(int t=0;t<8;t++){auto found=lookup.find(transform(a[i],t));if(found==lookup.end())return 2;rep[i]=min(rep[i],found->second);}}
 uint64_t edges=0;for(int i=0;i<m;i++)for(int j=0;j<i;j++){bool disjoint=true;for(int r=0;r<n;r++)if(a[i][r]==a[j][r]){disjoint=false;break;}if(disjoint){adj[i][j>>6]|=1ULL<<(j&63);adj[j][i>>6]|=1ULL<<(i&63);edges++;}}
 vector<int> roots;for(int i=0;i<m;i++)if(rep[i]==i)roots.push_back(i);
 filesystem::create_directories(prefix+".parts");vector<RootJob> jobs(roots.size());for(int k=0;k<(int)roots.size();k++)jobs[k].file=prefix+".parts/r"+to_string(k)+".proof.gz";
 started=chrono::steady_clock::now();auto common_start=started;atomic<int> next{0};atomic<bool> found{false};mutex publication;vector<int> solution;
 cerr<<"order="<<n<<" vertices="<<m<<" edges="<<edges<<" target="<<target<<" threads="<<workers<<"\n";
 vector<thread> threads;
 for(int worker=0;worker<workers;worker++)threads.emplace_back([&,worker]{
  started=common_start;
  while(!search_stop.load(memory_order_relaxed)){
   if(elapsed()>limitsec){search_stop=true;break;}
   int k=next.fetch_add(1);if(k>=(int)roots.size())break;int i=roots[k];
   nodes=0;timeout=false;root_cut=false;stop_reason.clear();path={i};answer.clear();best_lower=0;matching_checks=matching_cuts=repair_attempts=repair_used=repair_closed=0;
   output_prefix=prefix+".parts/r"+to_string(k);proof=gzopen(jobs[k].file.c_str(),"wb1");if(!proof){search_stop=true;return;}
   Bits candidates=adj[i];for(int j=0;j<m;j++)if(j<=i||rep[j]<i)clearbit(candidates,j);
   bool hit=expand(candidates);gzclose(proof);proof=nullptr;jobs[k].nodes=nodes;jobs[k].done=!hit&&!timeout&&!root_cut;
   if(hit){lock_guard<mutex> hold(publication);if(!found.load()){solution=answer;found=true;}search_stop=true;}
   else if(timeout||root_cut)search_stop=true;
   {lock_guard<mutex> hold(publication);cerr<<"completed ordinal="<<k<<" catalogue="<<i<<" node_count="<<nodes<<" closed="<<jobs[k].done<<" seconds="<<elapsed()<<"\n";}
  }
 });
 for(auto& worker:threads)worker.join();bool all=true;uint64_t total=0;int completed=0;for(auto& job:jobs){all=all&&job.done;completed+=job.done;total+=job.nodes;}
 string status=found?"SAT":all?"EXHAUSTED":"TIMEOUT";
 if(found)save_witness(solution,prefix+".witness.json");
 if(all&&!found){
  ofstream combined(prefix+".proof.gz",ios::binary);ofstream boundaries(prefix+".boundaries.txt");uint64_t count=0;
  for(int k=0;k<(int)jobs.size();k++){ifstream piece(jobs[k].file,ios::binary);if(!piece){cerr<<"missing root proof\n";return 3;}combined<<piece.rdbuf();count+=jobs[k].nodes;boundaries<<k+1<<" "<<count<<"\n";if((k+1)%20==0)cerr<<"roots="<<k+1<<" last="<<roots[k]<<" nodes="<<count<<" seconds="<<elapsed()<<"\n";}
  combined.close();boundaries.close();gzFile ending=gzopen((prefix+".proof.gz").c_str(),"ab1");if(!ending)return 3;gzwrite(ending,"ENDPROOF",8);gzclose(ending);
 }
 ofstream report(prefix+".json");report<<"{\"order\":"<<n<<",\"target\":"<<target<<",\"vertices\":"<<m<<",\"edges\":"<<edges<<",\"nodes\":"<<total<<",\"roots\":"<<roots.size()<<",\"completed_roots\":"<<completed<<",\"threads\":"<<workers<<",\"seconds\":"<<elapsed()<<",\"status\":\""<<status<<"\"}\n";
 cerr<<status<<" total_nodes="<<total<<" seconds="<<elapsed()<<"\n";return 0;
}
'''
Path('clique_threaded.cpp').write_text('// Parallel independent-root search: one process, at most three threads.\n'+s)
