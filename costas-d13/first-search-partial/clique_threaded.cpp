// Parallel independent-root search: one process, at most three threads.
// Catalogue clique decision search. Compiled as C++17, one thread.
// Independent witness/exclusion validation is in separate Python code.
#include <algorithm>
#include <atomic>
#include <thread>
#include <mutex>
#include <filesystem>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
#include <zlib.h>
#include <sys/statvfs.h>
using namespace std;
using Bits=vector<uint64_t>;
atomic<bool> search_stop{false};
int n,m,W,target;
vector<vector<int>> a,partition_keys;
vector<Bits> adj;
vector<int> rep;
thread_local vector<int> path,answer;
thread_local uint64_t nodes=0;
thread_local uint64_t matching_checks=0,matching_cuts=0;
thread_local uint64_t repair_attempts=0,repair_used=0,repair_closed=0;
thread_local string output_prefix;
thread_local int best_lower=0;
void save_witness(const vector<int>& vertices,const string& filename){
 ofstream w(filename);w<<"{\"order\":"<<n<<",\"size\":"<<vertices.size()<<",\"index_base\":0,\"catalogue_row_indices\":[";
 for(int i=0;i<(int)vertices.size();i++)w<<(i?",":"")<<vertices[i];w<<"],\"arrays\":[";
 for(int i=0;i<(int)vertices.size();i++){w<<(i?",[":"[");for(int r=0;r<n;r++)w<<(r?",":"")<<a[vertices[i]][r];w<<"]";}w<<"]}\n";
}
atomic<double> limitsec{0.0};
thread_local bool timeout=false;
thread_local string stop_reason;
thread_local double slice_seconds=0,root_started=0;
thread_local bool root_cut=false;
thread_local gzFile proof=nullptr;
thread_local gzFile replay_input=nullptr;
thread_local bool replaying=false;
thread_local uint64_t replayed_nodes=0;
thread_local string replay_path;
thread_local string time_control;
void emit(unsigned char c){if(proof && gzwrite(proof,&c,1)!=1){cerr<<"proof write failed\n";exit(3);}}
bool hole_matching_cut(const vector<int>& verts,const vector<uint32_t>& support){
#ifdef DISABLE_HOLE_MATCHING
 return false;
#endif
 if(target!=n-1 || n>31)return false;
 uint32_t full=(1U<<n)-1;vector<uint32_t> used(n),allowed(n);int forced=0;
 for(int v:path)for(int r=0;r<n;r++)used[r]|=1U<<a[v][r];
 for(int r=0;r<n;r++){
  uint32_t vacant=full&~used[r],missing=vacant&~support[r];
  if(__builtin_popcount(missing)>1)return false; // ordinary row bound handles this
  allowed[r]=missing?missing:vacant;forced+=(missing!=0);
 }
 if(forced<2)return false;
 matching_checks++;vector<int> owner(n,-1);uint32_t reached_rows=0,reached_cols=0;
 function<bool(int)> augment=[&](int row){
  reached_rows|=1U<<row;uint32_t available=allowed[row]&~reached_cols;
  while(available){int c=__builtin_ctz(available);available&=available-1;if(reached_cols>>c&1)continue;reached_cols|=1U<<c;
   if(owner[c]<0 || augment(owner[c])){owner[c]=row;return true;}
  }return false;
 };
 for(int r=0;r<n;r++){
  reached_rows=reached_cols=0;if(augment(r))continue;
  uint32_t neighbors=0;for(int s=0;s<n;s++)if(reached_rows>>s&1)neighbors|=allowed[s];
  if(__builtin_popcount(neighbors)>=__builtin_popcount(reached_rows)){cerr<<"bad Hall cut\n";exit(4);}
  matching_cuts++;emit(252);for(int b=0;b<4;b++)emit((reached_rows>>(8*b))&255);
  if(matching_cuts==1){
   ofstream sample(output_prefix+".hall.json");sample<<"{\"order\":"<<n<<",\"target\":"<<target<<",\"hall_rows_mask\":"<<reached_rows<<",\"selected\":[";
   for(int j=0;j<(int)path.size();j++)sample<<(j?",":"")<<path[j];sample<<"],\"candidates\":[";
   for(int j=0;j<(int)verts.size();j++)sample<<(j?",":"")<<verts[j];sample<<"]}\n";
  }
  return true;
 }return false;
}
thread_local chrono::steady_clock::time_point started;
double elapsed(){return chrono::duration<double>(chrono::steady_clock::now()-started).count();}
bool empty(const Bits& p){for(auto w:p)if(w)return false;return true;}
int first(const Bits& p){for(int j=0;j<W;j++)if(p[j])return j*64+__builtin_ctzll(p[j]);return -1;}
void clearbit(Bits& p,int v){p[v>>6]&=~(1ULL<<(v&63));}
int pop(const Bits& p){int z=0;for(auto w:p)z+=__builtin_popcountll(w);return z;}
Bits intersect(const Bits& p,const Bits& q){Bits r(W);for(int j=0;j<W;j++)r[j]=p[j]&q[j];return r;}
// Greedy proper colouring: each colour class is an independent set.
void greedy_colour(const Bits& p,vector<int>& order,vector<int>& bounds){
 vector<int> nonzero;for(int j=0;j<W;j++)if(p[j])nonzero.push_back(j);
 auto next=[&](const Bits& b){for(int j:nonzero)if(b[j])return j*64+__builtin_ctzll(b[j]);return -1;};
 Bits left=p;int col=0;
 while(next(left)>=0){
  ++col;Bits avail=left;int v;
  while((v=next(avail))>=0){
   order.push_back(v);bounds.push_back(col);
   clearbit(left,v);clearbit(avail,v);
   for(int j:nonzero)avail[j]&=~adj[v][j];
  }
 }
}
void row_colour(const Bits& p,int row,vector<int>& order,vector<int>& bounds){
 vector<vector<int>> groups(n);
 for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int b=__builtin_ctzll(w),v=64*j+b;groups[partition_keys[v][row]].push_back(v);w&=w-1;}}
 groups.erase(remove_if(groups.begin(),groups.end(),[](auto&g){return g.empty();}),groups.end());
 sort(groups.begin(),groups.end(),[](auto&x,auto&y){return x.size()!=y.size()?x.size()>y.size():x.front()<y.front();});
 int c=0;for(auto&g:groups){++c;for(int v:g){order.push_back(v);bounds.push_back(c);}}
}
struct RepairColouring {
 vector<int> vertices,which;
 vector<vector<int>> classes;
 RepairColouring(const vector<int>& verts,const vector<int>& order,const vector<int>& bounds):vertices(verts),which(verts.size()),classes(bounds.empty()?0:bounds.back()){
  for(int i=0;i<(int)order.size();i++){int v=lower_bound(vertices.begin(),vertices.end(),order[i])-vertices.begin();classes[bounds[i]-1].push_back(v);which[v]=bounds[i]-1;}
 }
 bool allowed(int v,int dest)const{for(int u:classes[dest])if(adj[vertices[v]][vertices[u]>>6]>>(vertices[u]&63)&1)return false;return true;}
 void move(int v,int dest){int old=which[v];auto& group=classes[old];auto it=find(group.begin(),group.end(),v);if(it==group.end()){cerr<<"bad recolouring member\n";exit(6);}group.erase(it);classes[dest].push_back(v);which[v]=dest;}
 void flatten(vector<int>& order,vector<int>& bounds){order.clear();bounds.clear();int colour=0;for(auto& group:classes)if(!group.empty()){colour++;sort(group.begin(),group.end());for(int v:group){order.push_back(vertices[v]);bounds.push_back(colour);}}}
};
bool repaired_colour(const vector<int>& verts,const vector<int>& go,const vector<int>& gb,int need,vector<int>& order,vector<int>& bounds,vector<pair<int,int>>& moves){
 if(verts.size()>64 || gb.empty() || need<3 || gb.back()<need || gb.back()>need+1)return false;
 repair_attempts++;RepairColouring state(verts,go,gb);
 auto change=[&](int v,int dest){if(!state.allowed(v,dest)){cerr<<"invalid recolouring\n";exit(6);}state.move(v,dest);moves.emplace_back(v,dest);};
 for(int colour=(int)state.classes.size()-1;colour>=need-1;colour--){
  auto pending=state.classes[colour];
  for(int x:pending){
   if(state.which[x]!=colour)continue;bool done=false;
   for(int low=0;low<need-1 && !done;low++){
    int conflict=-1,count=0;for(int y:state.classes[low])if(adj[verts[x]][verts[y]>>6]>>(verts[y]&63)&1){conflict=y;if(++count>1)break;}
    if(count==0){change(x,low);done=true;break;}
    if(count==1)for(int other=low+1;other<need-1;other++)if(state.allowed(conflict,other)){change(conflict,other);change(x,low);done=true;break;}
   }
  }
 }
 if(moves.empty())return false;state.flatten(order,bounds);return true;
}
bool decode_replay(const Bits& p,int need,vector<int>& order,vector<int>& bounds,bool& closed){
 if(!replaying)return false;
 int op=gzgetc(replay_input);
 if(op<0){
  int code;gzerror(replay_input,&code);if(code!=Z_OK && code!=Z_STREAM_END){cerr<<"bad replay gzip\n";exit(5);}
  gzclose(replay_input);replay_input=nullptr;replaying=false;
  proof=gzopen((output_prefix+".proof.gz").c_str(),"ab1");if(!proof)exit(5);
  cerr<<"replay_finished nodes="<<replayed_nodes<<" seconds="<<elapsed()<<"\n";
  return false;
 }
 replayed_nodes++;
 if(op==253){if(pop(p)>=need){cerr<<"invalid cardinality in replay\n";exit(5);}closed=true;return true;}
 if(op==252){cerr<<"resumption currently requires a trace without matching cuts\n";exit(5);}
 if(op==251){
  vector<int> vertices;for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int b=__builtin_ctzll(w);vertices.push_back(64*j+b);w&=w-1;}}
  if(vertices.size()>64){cerr<<"oversized recolouring node\n";exit(5);}
  greedy_colour(p,order,bounds);RepairColouring state(vertices,order,bounds);int count=gzgetc(replay_input);if(count<0)exit(5);
  for(int i=0;i<count;i++){int v=gzgetc(replay_input),dest=gzgetc(replay_input);if(v<0||v>=(int)vertices.size()||dest<0||dest>=(int)state.classes.size()||!state.allowed(v,dest)){cerr<<"invalid replay recolouring\n";exit(5);}state.move(v,dest);}
  state.flatten(order,bounds);
 }
 else if(op==254)greedy_colour(p,order,bounds);
 else if(op<2*n)row_colour(p,op,order,bounds);
 else{cerr<<"invalid replay opcode "<<op<<"\n";exit(5);}
 return true;
}
bool inspect_lower(const Bits& p){
 if(best_lower>=target-1 || (int)path.size()<target-3)return false;
 vector<int> trial=path;Bits q=p;
 while(!empty(q) && (int)trial.size()<target){int v=first(q);trial.push_back(v);q=intersect(q,adj[v]);}
 if((int)trial.size()>best_lower){best_lower=trial.size();save_witness(trial,output_prefix+".lower.witness.json");cerr<<"lower_witness="<<best_lower<<" nodes="<<nodes<<" seconds="<<elapsed()<<"\n";}
 if((int)trial.size()>=target){answer=trial;return true;}return false;
}
// Each cell of a fixed row is an independent set. Prefer the partition
// whose eligible suffix (colours >= need) contains the fewest vertices.
// This includes MRV exact-cover branching when all colours are required.
void colour(const Bits& p,vector<int>& order,vector<int>& bounds,int need){
 vector<int> verts;verts.reserve(pop(p));
 for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int b=__builtin_ctzll(w);verts.push_back(64*j+b);w&=w-1;}}
 int bestscore=1000000000,bestrow=0;vector<int> sizes(n),positive;vector<uint32_t> support(n);
 for(int r=0;r<2*n;r++){
  fill(sizes.begin(),sizes.end(),0);for(int v:verts)sizes[partition_keys[v][r]]++;
  if(r<n)for(int c=0;c<n;c++)if(sizes[c])support[r]|=1U<<c;
  positive.clear();for(int z:sizes)if(z)positive.push_back(z);
  if((int)positive.size()<need){bestscore=-1;bestrow=r;break;}
  sort(positive.begin(),positive.end(),greater<int>());
  int score=0;for(int c=max(0,need-1);c<(int)positive.size();c++)score+=positive[c];
  if(score<bestscore){bestscore=score;bestrow=r;}
 }
 if(bestscore>=0 && hole_matching_cut(verts,support))return;
 vector<int> go,gb;if(bestscore>=0)greedy_colour(p,go,gb);
 int gscore=0;for(int b:gb)if(b>=need)gscore++;
#ifdef ENABLE_COLOUR_REPAIR
 if(bestscore>0 && gscore>0){
  vector<int> ro,rb;vector<pair<int,int>> moves;
  if(repaired_colour(verts,go,gb,need,ro,rb,moves)){
   int score=0;for(int b:rb)if(b>=need)score++;
   if(score<gscore && score<bestscore){
    if(moves.size()>255){cerr<<"too many recolouring moves\n";exit(6);}repair_used++;if(score==0)repair_closed++;
    emit(251);emit((unsigned char)moves.size());for(auto move:moves){emit((unsigned char)move.first);emit((unsigned char)move.second);}
    order=std::move(ro);bounds=std::move(rb);return;
   }
  }
 }
#endif
 if(gscore<bestscore){emit(254);order=std::move(go);bounds=std::move(gb);return;}
 emit((unsigned char)bestrow);
 row_colour(p,bestrow,order,bounds);
}
bool enter_node(){
 if(search_stop.load(memory_order_relaxed)){timeout=true;stop_reason="peer_stop";return false;}
 ++nodes;
 if((int)path.size()>=target-2 && (int)path.size()>best_lower){
  best_lower=path.size();save_witness(path,output_prefix+".lower.witness.json");
  cerr<<"lower_witness="<<best_lower<<" nodes="<<nodes<<" seconds="<<elapsed()<<"\n";
 }
 if(slice_seconds>0 && (nodes&1023)==0 && elapsed()-root_started>slice_seconds){root_cut=true;return false;}
 if((nodes&16383)==0){
  if(!time_control.empty()){
   ifstream control(time_control);double cap;
   if(control>>cap && isfinite(cap) && cap>=0 && cap!=limitsec){limitsec=cap;cerr<<"time_limit_updated="<<limitsec<<" seconds="<<elapsed()<<"\n";}
  }
  if(elapsed()>limitsec){timeout=true;stop_reason="time_limit";return false;}
  struct statvfs fs;if(statvfs(".",&fs)==0 && (uint64_t)fs.f_bavail*fs.f_frsize<3ULL*1024*1024*1024){timeout=true;stop_reason="disk_below_3GiB";return false;}
  if(proof && gzoffset(proof)>800LL*1024*1024){timeout=true;stop_reason="proof_cap_800MiB";return false;}
 }
 if((nodes&1048575)==0)cerr<<"nodes="<<nodes<<" root="<<path.front()<<" depth="<<path.size()<<" seconds="<<elapsed()<<"\n";
 return true;
}

#ifdef ENABLE_SMALL_KERNEL
#include "small_early.hpp"
#endif

bool expand(Bits p){
#ifdef ENABLE_SMALL_KERNEL
 if(pop(p)<=128){int vertices[128],len=0;for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int v=64*j+__builtin_ctzll(w);w&=w-1;vertices[len++]=v;}}return expand_small_vector(vertices,len);}
#endif
 if(!enter_node())return false;
 int need=target-(int)path.size();
 if(!need){answer=path;return true;}
 if(inspect_lower(p))return true;
 vector<int> order,bounds;order.reserve(pop(p));bounds.reserve(order.capacity());
 bool closed=false,decoded=decode_replay(p,need,order,bounds,closed);
 if(closed)return false;
 if(!decoded){if(pop(p)<need){emit(253);return false;}colour(p,order,bounds,need);}
 for(int k=(int)order.size()-1;k>=0;k--){
  if(bounds[k]<need)return false;
  int v=order[k];path.push_back(v);
  if(need==1){answer=path;return true;}
  if(expand(intersect(p,adj[v])))return true;
  path.pop_back();if(timeout||root_cut)return false;
  clearbit(p,v);
 }
 return false;
}
vector<int> transform(const vector<int>& x,int t){
 vector<int> y(n);for(int r=0;r<n;r++){
  int u=r,v=x[r];if(t&4)swap(u,v);
  if(t&1)u=n-1-u;if(t&2)v=n-1-v;y[u]=v;
 }return y;
}

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
  started=common_start;time_control=prefix+".time-limit";
  while(!search_stop.load(memory_order_relaxed)){
   {ifstream control(time_control);double revised;if(control>>revised && isfinite(revised) && revised>=0)limitsec=revised;}
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

 {ofstream ledger(prefix+".roots.json");ledger<<"{\"generator_status_only\":true,\"order\":"<<n<<",\"target\":"<<target<<",\"jobs\":[";
  for(int k=0;k<(int)jobs.size();k++)ledger<<(k?",":"")<<"{\"ordinal\":"<<k<<",\"catalogue_index\":"<<roots[k]<<",\"complete_negative\":"<<(jobs[k].done?"true":"false")<<",\"nodes\":"<<jobs[k].nodes<<",\"proof\":\""<<jobs[k].file<<"\"}";
  ledger<<"]}\n";}
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
