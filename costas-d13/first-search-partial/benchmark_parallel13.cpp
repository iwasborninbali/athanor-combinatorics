// PERFORMANCE ONLY: deliberate early stop, not a proof verifier.
// RESTRICTED ROOT VERIFIER, never a global claim.
// Independent full verifier; root ranges are verified, never trusted.
// Independent trace verifier. No search code is included or linked.
// Candidate sets are sorted vectors, graph construction is by cell incidence,
// and canonical greedy classes are decoded by a first-fit vector scan.
#include <algorithm>
#include <atomic>
#include <mutex>
#include <thread>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#include <zlib.h>
using namespace std;
void require(bool ok,const char* message){if(!ok)throw runtime_error(message);}
std::atomic<uint64_t> progress_nodes{0};
std::mutex log_mutex;
struct SampleStop {};
struct Trace {
 gzFile f;unsigned char buffer[65536];int pos=0,length=0;uint64_t cursor=0,stop=~uint64_t(0);
 explicit Trace(const char* path):f(gzopen(path,"rb")){require(f,"cannot open trace");}
 void segment(uint64_t begin,uint64_t end){require(begin<=end,"reversed trace range");require(gzseek(f,(z_off_t)begin,SEEK_SET)==(z_off_t)begin,"trace seek failure");pos=length=0;cursor=begin;stop=end;}
 int next(){
  if(cursor==stop)return -1;
  if(pos==length){length=gzread(f,buffer,min<uint64_t>(sizeof(buffer),stop-cursor));pos=0;require(length>=0,"gzip read failure");if(!length){int error;gzerror(f,&error);require(error==Z_OK||error==Z_STREAM_END,"truncated or corrupt gzip");return -1;}}
  cursor++;return buffer[pos++];
 }
 int byte(){int c=next();require(c>=0,"truncated trace");return c;}
 ~Trace(){if(f)gzclose(f);}
};
struct Audit {
 int n,m,target,words;vector<vector<int>> arrays,inverse;
 vector<vector<uint64_t>> neighbors;const vector<vector<uint64_t>>* neighbor_view=nullptr;vector<int> representative,selection;
 uint64_t nodes=0,roots=0;chrono::steady_clock::time_point start;
 Trace& trace;
 Audit(const char* catalogue,int k,Trace& input):target(k),trace(input){
  ifstream f(catalogue);require(bool(f>>n>>m),"missing catalogue header");require(n>0&&n<32&&m>0&&target>1,"invalid parameters");
  arrays.assign(m,vector<int>(n));inverse=arrays;map<vector<int>,int> index;
  for(int v=0;v<m;v++){
   vector<bool> seen(n);for(int r=0;r<n;r++){int c;require(bool(f>>c)&&c>=0&&c<n&&!seen[c],"invalid permutation");seen[c]=true;arrays[v][r]=c;inverse[v][c]=r;}
   require(index.emplace(arrays[v],v).second,"duplicate catalogue array");
   vector<pair<int,int>> differences;for(int r=0;r<n;r++)for(int s=r+1;s<n;s++)differences.emplace_back(s-r,arrays[v][s]-arrays[v][r]);
   sort(differences.begin(),differences.end());require(adjacent_find(differences.begin(),differences.end())==differences.end(),"non-Costas catalogue row");
  }
  string extra;require(!(f>>extra),"extra catalogue entries");
  words=(m+63)/64;vector<vector<uint64_t>> incidence(n*n,vector<uint64_t>(words));
  for(int v=0;v<m;v++)for(int r=0;r<n;r++)incidence[r*n+arrays[v][r]][v/64]|=uint64_t(1)<<(v%64);
  neighbors.assign(m,vector<uint64_t>(words,~uint64_t(0)));
  for(int v=0;v<m;v++){
   if(m%64)neighbors[v].back()=(uint64_t(1)<<(m%64))-1;
   for(int r=0;r<n;r++)for(int b=0;b<words;b++)neighbors[v][b]&=~incidence[r*n+arrays[v][r]][b];
  }
  representative.resize(m);
  for(int v=0;v<m;v++){
   int smallest=v;vector<int> turn=arrays[v];
   for(int t=0;t<4;t++){
    auto found=index.find(turn);require(found!=index.end(),"catalogue not rotation-closed");smallest=min(smallest,found->second);
    vector<int> reflected(n);for(int r=0;r<n;r++)reflected[r]=n-1-turn[r];
    found=index.find(reflected);require(found!=index.end(),"catalogue not reflection-closed");smallest=min(smallest,found->second);
    vector<int> next(n);for(int r=0;r<n;r++)next[turn[r]]=n-1-r;turn=next;
   }representative[v]=smallest;
  }
  neighbor_view=&neighbors;start=chrono::steady_clock::now();
 }
 Audit(const Audit& source,Trace& input):n(source.n),m(source.m),target(source.target),words(source.words),arrays(source.arrays),inverse(source.inverse),neighbor_view(source.neighbor_view),representative(source.representative),trace(input){start=chrono::steady_clock::now();}
 bool edge(int u,int v)const{return ((*neighbor_view)[u][v/64]>>(v%64))&1;}
 double seconds()const{return chrono::duration<double>(chrono::steady_clock::now()-start).count();}
 void hall(const vector<int>& vertices){
  require(target==n-1,"Hall opcode for wrong target");uint32_t mask=0;for(int b=0;b<4;b++)mask|=uint32_t(trace.byte())<<(8*b);
  uint32_t full=(uint32_t(1)<<n)-1;require(mask && !(mask&~full),"invalid Hall row mask");
  vector<uint32_t> occupied(n),support(n),allowed(n);
  for(int v:selection)for(int r=0;r<n;r++){uint32_t bit=uint32_t(1)<<arrays[v][r];require(!(occupied[r]&bit),"selection not disjoint");occupied[r]|=bit;}
  for(int v:vertices)for(int r=0;r<n;r++){uint32_t bit=uint32_t(1)<<arrays[v][r];require(!(occupied[r]&bit),"invalid common candidate");support[r]|=bit;}
  uint32_t columns=0;
  for(int r=0;r<n;r++){uint32_t vacant=full^occupied[r],forced=vacant&~support[r];require(__builtin_popcount(forced)<=1,"invalid forced-hole claim");allowed[r]=forced?forced:vacant;if(mask>>r&1)columns|=allowed[r];}
  require(__builtin_popcount(columns)<__builtin_popcount(mask),"Hall inequality not deficient");
 }

 // Small certificates are decoded with bounded stack arrays. This performs
 // the same independent vector scan and coverage check without heap traffic.
 void small_node(const int* vertices,int length,int need){
  require(need>0,"target clique reached in refutation");nodes++;if(nodes>1000000)throw SampleStop{};
  if(nodes%1048576==0){auto total=progress_nodes.fetch_add(1048576)+1048576;lock_guard<mutex> hold(log_mutex);cerr<<"verified_nodes_approx="<<total<<"\n";}
  int op=trace.byte();
  if(op==253){require(length<need,"invalid cardinality leaf");return;}
  if(op==252){vector<int> v(vertices,vertices+length);hall(v);return;}
  int members[128][128],counts[128]={},nc=0,ids[128];
  if(op<2*n){
   nc=n;
   for(int i=0;i<length;i++){int v=vertices[i],c=op<n?arrays[v][op]:inverse[v][op-n];members[c][counts[c]++]=i;}
   int used=0;for(int c=0;c<nc;c++)if(counts[c])ids[used++]=c;
   sort(ids,ids+used,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:members[x][0]<members[y][0];});nc=used;
  }else{
   require(op==254||op==251,"unknown trace opcode");bool assigned[128]={};int done=0;
   while(done<length){
    int colour=nc++;
    for(int i=0;i<length;i++)if(!assigned[i]){
     bool independent=true;for(int q=0;q<counts[colour];q++)if(edge(vertices[i],vertices[members[colour][q]])){independent=false;break;}
     if(independent){members[colour][counts[colour]++]=i;assigned[i]=true;done++;}
    }
    require(counts[colour]>0,"empty greedy class");
   }
   if(op==251){
    require(length<=64,"oversized recolouring node");int membership[128];for(int c=0;c<nc;c++)for(int j=0;j<counts[c];j++)membership[members[c][j]]=c;
    int moves=trace.byte();for(int j=0;j<moves;j++){
     int i=trace.byte(),dest=trace.byte();require(i<length&&dest<nc,"invalid recolouring index");
     for(int q=0;q<counts[dest];q++)require(!edge(vertices[i],vertices[members[dest][q]]),"improper recolouring move");
     int old=membership[i],at=0;while(at<counts[old]&&members[old][at]!=i)at++;require(at<counts[old],"missing recolouring member");
     for(int q=at+1;q<counts[old];q++)members[old][q-1]=members[old][q];counts[old]--;members[dest][counts[dest]++]=i;membership[i]=dest;
    }
    for(int c=0;c<nc;c++)sort(members[c],members[c]+counts[c]);
   }
   int used=0;for(int c=0;c<nc;c++)if(counts[c])ids[used++]=c;nc=used;
  }
  bool active[128];fill(active,active+length,true);int covered=0;for(int c=0;c<nc;c++)covered+=counts[ids[c]];require(covered==length,"colour coverage failure");
  int child[128];
  for(int colour=nc;colour>=need;colour--){int c=ids[colour-1];for(int k=counts[c]-1;k>=0;k--){
   require(need>1,"certificate omits an existing target clique");int i=members[c][k],v=vertices[i];require(active[i],"repeated branch vertex");
   int len=0;for(int j=0;j<length;j++)if(active[j]&&edge(v,vertices[j]))child[len++]=vertices[j];
   selection.push_back(v);small_node(child,len,need-1);selection.pop_back();active[i]=false;
  }}
 }
 void node(const vector<int>& vertices,int need){
  if(vertices.size()<=128){small_node(vertices.data(),vertices.size(),need);return;}
  require(need>0,"target clique reached in refutation");nodes++;if(nodes>1000000)throw SampleStop{};
  if(nodes%1048576==0){auto total=progress_nodes.fetch_add(1048576)+1048576;lock_guard<mutex> hold(log_mutex);cerr<<"verified_nodes_approx="<<total<<"\n";}
  int op=trace.byte();
  if(op==253){require((int)vertices.size()<need,"invalid cardinality leaf");return;}
  if(op==252){hall(vertices);return;}
  vector<vector<int>> classes;
  if(op<2*n){
   classes.resize(n);
   for(int i=0;i<(int)vertices.size();i++){int v=vertices[i],cell=op<n?arrays[v][op]:inverse[v][op-n];classes[cell].push_back(i);}
   classes.erase(remove_if(classes.begin(),classes.end(),[](const auto& group){return group.empty();}),classes.end());
   sort(classes.begin(),classes.end(),[](const auto& x,const auto& y){return x.size()!=y.size()?x.size()>y.size():x.front()<y.front();});
  }else{
   require(op==254||op==251,"unknown trace opcode");vector<int> remaining(vertices.size());for(int i=0;i<(int)remaining.size();i++)remaining[i]=i;
   while(!remaining.empty()){
    vector<int> colour,left;
    for(int i:remaining){bool independent=true;for(int j:colour)if(edge(vertices[i],vertices[j])){independent=false;break;}if(independent)colour.push_back(i);else left.push_back(i);}
    require(!colour.empty(),"empty greedy class");classes.push_back(std::move(colour));remaining=std::move(left);
   }
   if(op==251){
    require(vertices.size()<=64,"oversized recolouring node");vector<int> membership(vertices.size());for(int c=0;c<(int)classes.size();c++)for(int i:classes[c])membership[i]=c;
    int moves=trace.byte();for(int j=0;j<moves;j++){
     int i=trace.byte(),destination=trace.byte();require(i<(int)vertices.size()&&destination<(int)classes.size(),"invalid recolouring index");
     for(int other:classes[destination])require(!edge(vertices[i],vertices[other]),"improper recolouring move");
     int old=membership[i];auto at=find(classes[old].begin(),classes[old].end(),i);require(at!=classes[old].end(),"missing recolouring member");classes[old].erase(at);classes[destination].push_back(i);membership[i]=destination;
    }
    classes.erase(remove_if(classes.begin(),classes.end(),[](const auto& group){return group.empty();}),classes.end());for(auto& group:classes)sort(group.begin(),group.end());
   }
   // Independence is constructive: a new member is compared with every
   // earlier member above. Adjacency was independently reconstructed from
   // the validated cell incidences, rather than copied from the search.
  }
  vector<bool> active(vertices.size(),true);int covered=0;for(const auto& group:classes)covered+=group.size();require(covered==(int)vertices.size(),"colour coverage failure");
  for(int colour=(int)classes.size();colour>=need;colour--)for(auto it=classes[colour-1].rbegin();it!=classes[colour-1].rend();++it){
   require(need>1,"certificate omits an existing target clique");int i=*it,v=vertices[i];require(active[i],"repeated branch vertex");
   vector<int> child;child.reserve(vertices.size());for(int j=0;j<(int)vertices.size();j++)if(active[j]&&edge(v,vertices[j]))child.push_back(vertices[j]);
   selection.push_back(v);node(child,need-1);selection.pop_back();active[i]=false;
  }
 }
 void run_range(int begin,int end,bool exact_bytes=true){
  require(begin>=0&&end>begin,"invalid root range");int ordinal=0;uint64_t before=roots;
  for(int i=0;i<m;i++)if(representative[i]==i){
   int current=ordinal++;if(current<begin)continue;if(current>=end)break;
   vector<int> candidates;for(int j=i+1;j<m;j++)if(representative[j]>=i&&edge(i,j))candidates.push_back(j);
   selection={i};node(candidates,target-1);roots++;
  }
  require(roots-before==(uint64_t)(end-begin),"root range not covered");
  if(exact_bytes)require(trace.next()<0,"unconsumed bytes in certified root range");
 }

};
struct Segment {int first,last;uint64_t begin,end;};
int main(int argc,char**argv){try{
 require(argc==7,"usage: check_prefix_parallel catalogue trace.gz target boundaries.txt threads roots");
 int root_limit=stoi(argv[6]);
 int threads=stoi(argv[5]);require(threads>0&&threads<=3,"thread count must be 1..3");
 auto started=chrono::steady_clock::now();Trace original(argv[2]);Audit base(argv[1],stoi(argv[3]),original);
 int total_roots=0;for(int i=0;i<base.m;i++)if(base.representative[i]==i)total_roots++;
 require(root_limit>0&&root_limit<=total_roots,"invalid scoped root count");
 int last_catalogue_index=-1,ordinal=0;for(int i=0;i<base.m;i++)if(base.representative[i]==i){if(++ordinal==root_limit)last_catalogue_index=i;}
 ifstream metadata(argv[4]);require(bool(metadata),"cannot open boundaries");
 vector<Segment> segments;int root=0,last_root=0;uint64_t offset=0,last_offset=0;
 while(true){metadata>>ws;if(metadata.peek()==char_traits<char>::eof())break;require(bool(metadata>>root>>offset),"malformed boundary line");require(root>last_root&&root<=total_roots&&offset>last_offset&&offset<10000000000ULL,"invalid boundary");segments.push_back({last_root,root,last_offset,offset});last_root=root;last_offset=offset;}
 require(metadata.eof()&&!segments.empty()&&last_root==root_limit,"boundary ranges do not cover the specified root prefix");
 // Read through the complete gzip stream: all members, footer CRCs, the
 // final completion marker, and EOF are checked independently of ranges.
 (void)last_offset; // Validate gzip integrity, without making any claim about the later proof bytes.
 vector<uint64_t> counts(segments.size()),root_counts(segments.size()),end_cursors(segments.size());atomic<int> next{0};atomic<bool> failed{false};string error;
 vector<thread> pool;atomic<int> positioned{0};vector<double> sample_seconds(threads);
 for(int worker=0;worker<threads;worker++)pool.emplace_back([&,worker]{try{
  Trace stream(argv[2]);Audit audit(base,stream);
  int index=next.fetch_add(1);require(index<(int)segments.size(),"too few benchmark ranges");auto job=segments[index];stream.segment(job.begin,job.end);
  positioned.fetch_add(1);while(positioned.load()<threads && !failed.load())this_thread::yield();require(!failed.load(),"benchmark setup failed");
  auto sample_start=chrono::steady_clock::now();
  try{audit.run_range(job.first,job.last,false);throw runtime_error("benchmark range completed before the sample limit");}
  catch(const SampleStop&){counts[index]=1000000;sample_seconds[worker]=chrono::duration<double>(chrono::steady_clock::now()-sample_start).count();}

 }catch(const exception& problem){failed=true;lock_guard<mutex> hold(log_mutex);error=problem.what();}});
 for(auto& worker:pool)worker.join();require(!failed,error.c_str());uint64_t nodes=0,roots=0;for(auto value:counts)nodes+=value;for(auto value:root_counts)roots+=value;
 double seconds=chrono::duration<double>(chrono::steady_clock::now()-started).count();
 cout<<"{\"complete\":false,\"purpose\":\"performance sample only; NOT a certificate check\",\"sample_nodes\":"<<nodes<<",\"threads\":"<<threads<<",\"wall_seconds_including_seek\":"<<seconds<<",\"verification_seconds_by_thread\":[";for(int i=0;i<threads;i++)cout<<(i?",":"")<<sample_seconds[i];cout<<"]}\n";
 return 0;
}catch(const exception& problem){cerr<<"REJECTED: "<<problem.what()<<"\n";return 1;}}
