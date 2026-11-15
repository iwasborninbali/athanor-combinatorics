// Independent exact Costas packing feasibility search. C++20, OpenMP optional.
// Build: g++ -O3 -std=c++20 -march=native -fopenmp exact.cpp -o exact
// Run:   ./exact N K SECONDS [THREADS]
// Returns EXHAUSTED if all canonical first-array roots are proved to fail,
// FOUND if a packing is found, INCOMPLETE if interrupted. Progress persists
// in checkpoints/n<N>k<K>/root_<id>.done, whose contents record node counts.
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <numeric>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;
namespace fs=std::filesystem;
using Clock=chrono::steady_clock;
static constexpr int MAXW=201; // enough for 12828 vertices
using Bits=array<uint64_t,MAXW>;
static inline int nextbit(const Bits &v,int W) {
  for(int w=0;w<W;w++) if(v[w]) return (w<<6)+std::countr_zero(v[w]);
  return -1;
}
static inline int sizebits(const Bits &v,int W){int s=0;for(int w=0;w<W;w++)s+=popcount(v[w]);return s;}
static inline void del(Bits &v,int i){v[i>>6]&=~(1ull<<(i&63));}
static inline void put(Bits &v,int i){v[i>>6]|=1ull<<(i&63);}
static inline bool contains(const Bits &v,int i){return (v[i>>6]>>(i&63))&1ull;}
struct Problem {
  int n,N,W;
  vector<array<uint8_t,16>> a;
  vector<Bits> adj;
  vector<int> roots;
  explicit Problem(int n):n(n){
    string f="catalogues/costas"+to_string(n)+".bin";
    ifstream in(f,ios::binary);
    if(!in) throw runtime_error("cannot read catalogue "+f);
    vector<uint8_t> b((istreambuf_iterator<char>(in)),{});
    if(b.size()%n) throw runtime_error("invalid catalogue size");
    N=b.size()/n;W=(N+63)/64;
    if(W>MAXW) throw runtime_error("MAXW too small");
    a.resize(N);
    for(int i=0;i<N;i++)for(int j=0;j<n;j++)a[i][j]=b[i*n+j];
    adj.resize(N);
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
      bool disjoint=true;
      for(int r=0;r<n;r++)if(a[i][r]==a[j][r]){disjoint=false;break;}
      if(disjoint){put(adj[i],j);put(adj[j],i);}
    }
    for(int i=0;i<N;i++) {
      auto p=a[i];
      auto minimum=p;
      for(int trans=0;trans<2;trans++){
        for(int reflr=0;reflr<2;reflr++)for(int reflc=0;reflc<2;reflc++){
          array<uint8_t,16> q{};
          for(int r=0;r<n;r++){
            int x=reflr?n-1-r:r;
            int y=reflc?n-1-p[r]:p[r];
            if(trans) q[y]=x; else q[x]=y;
          }
          if(lexicographical_compare(q.begin(),q.begin()+n,minimum.begin(),minimum.begin()+n))minimum=q;
        }
      }
      if(equal(minimum.begin(),minimum.begin()+n,p.begin())) roots.push_back(i);
    }
  }
};
struct Engine {
  const Problem &pr;
  int k,root;
  uint64_t nodes=0,leaves=0;
  atomic<bool> &stop, &found;
  Clock::time_point deadline;
  vector<int> solution;
  Engine(const Problem& pr,int k,int root,atomic<bool> &stop,atomic<bool>&found,Clock::time_point deadline)
  :pr(pr),k(k),root(root),stop(stop),found(found),deadline(deadline){solution.reserve(k);solution.push_back(root);}
  bool dfs(Bits cand,int need){
    ++nodes;
    if((nodes & 31)==0 && (stop.load(memory_order_relaxed)||found.load(memory_order_relaxed) || Clock::now()>deadline)) {
      stop.store(true,memory_order_relaxed);return false;
    }
    int sz=sizebits(cand,pr.W);
    if(sz<need)return false;
    // Necessary pigeonhole bound: each future array must use a different
    // column in every row. If fewer than 'need' columns remain represented
    // among candidates in any row, no extension exists.
    if(need>1 && sz<160){
      for(int r=0;r<pr.n;r++){
        uint32_t columns=0;
        for(int w=0;w<pr.W;w++){
          uint64_t x=cand[w];
          while(x){int v=w*64+countr_zero(x);columns|=(1u<<pr.a[v][r]);x&=x-1;}
        }
        if(popcount(columns)<need)return false;
      }
    }
    if(need==1){
      int v=nextbit(cand,pr.W);
      solution.push_back(v);
      return true;
    }
    // Proper coloring of compatibility graph, via greedy independent sets.
    // Clique number cannot exceed number of colors.
    vector<int> ordered; ordered.reserve(sz);
    vector<int> colors; colors.reserve(sz);
    Bits uncolored=cand;
    int color=0;
    while(true){
      if(nextbit(uncolored,pr.W)<0)break;
      ++color;
      Bits available=uncolored;
      while(true){
        if((ordered.size() & 63)==0 && (stop.load(memory_order_relaxed)||found.load(memory_order_relaxed)||Clock::now()>deadline)) {
          stop.store(true,memory_order_relaxed);return false;
        }
        int v=nextbit(available,pr.W);
        if(v<0)break;
        ordered.push_back(v);colors.push_back(color);
        del(uncolored,v);
        for(int w=0;w<pr.W;w++)available[w]&=~pr.adj[v][w];
        del(available,v);
      }
    }
    if(color<need) return false;
    // Explore in decreasing coloring order with a valid branch bound.
    for(int i=(int)ordered.size()-1;i>=0;i--){
      if(colors[i]<need)return false;
      int v=ordered[i];
      Bits next{};
      for(int w=0;w<pr.W;w++)next[w]=cand[w]&pr.adj[v][w];
      if(sizebits(next,pr.W)>=need-1){
        solution.push_back(v);
        if(dfs(next,need-1))return true;
        solution.pop_back();
      }
      del(cand,v);
      if(stop.load(memory_order_relaxed)||found.load(memory_order_relaxed))return false;
    }
    ++leaves;
    return false;
  }
  bool solve_second(int second){
    if(second<=root || !contains(pr.adj[root],second))return false;
    solution.push_back(second);
    Bits cand{};
    for(int j=second+1;j<pr.N;j++)
      if(contains(pr.adj[root],j) && contains(pr.adj[second],j))put(cand,j);
    bool ok=dfs(cand,k-2);
    if(!ok)solution.pop_back();
    return ok;
  }
  bool solve(){
    Bits cand{};
    for(int j=root+1;j<pr.N;j++)if(contains(pr.adj[root],j))put(cand,j);
    return dfs(cand,k-1);
  }
};
int main(int argc,char**argv){
  if(argc<4){cerr<<"usage: ./exact N K TIME_LIMIT_SECONDS [THREADS]\n";return 2;}
  int n=stoi(argv[1]),k=stoi(argv[2]);double seconds=stod(argv[3]);
  int threads=argc>4?stoi(argv[4]):1;
#ifdef _OPENMP
  omp_set_num_threads(threads);
#else
  threads=1;
#endif
  auto begin=Clock::now();
  Problem pr(n);
  cout<<"n="<<n<<" k="<<k<<" catalogue="<<pr.N<<" canonical_roots="<<pr.roots.size()
      <<" threads="<<threads<<" setup_seconds="<<chrono::duration<double>(Clock::now()-begin).count()<<endl;
  string dir="checkpoints/n"+to_string(n)+"k"+to_string(k);
  fs::create_directories(dir);
  int prefixroot=argc>5?stoi(argv[5]):-1;
  if(prefixroot>=0 && find(pr.roots.begin(),pr.roots.end(),prefixroot)==pr.roots.end()) {
    cerr<<"not a D4 canonical root: "<<prefixroot<<endl;return 2;
  }
  if(prefixroot>=0){
    // Resume at a finer-grained root+second-array branch.
    string subdir=dir+"/prefix_"+to_string(prefixroot);
    fs::create_directories(subdir);
    vector<int> seconds;
    for(int j=pr.N-1;j>prefixroot;j--)if(contains(pr.adj[prefixroot],j))seconds.push_back(j);
    atomic<bool> substop{false}, subfound{false};
    atomic<uint64_t> subnodes{0}; atomic<int> done{0},reused{0};
    mutex submu;
    auto subdeadline=Clock::now()+chrono::duration_cast<Clock::duration>(chrono::duration<double>(stod(argv[3])));
#pragma omp parallel for schedule(dynamic,1)
    for(int t=0;t<(int)seconds.size();t++){
      int second=seconds[t];
      string f=subdir+"/second_"+to_string(second)+".done";
      if(fs::exists(f)){done++;reused++;continue;}
      if(substop.load()||subfound.load()||Clock::now()>subdeadline){substop.store(true);continue;}
      Engine e(pr,k,prefixroot,substop,subfound,subdeadline);
      bool ok=e.solve_second(second);
      subnodes+=e.nodes;
      if(ok){
        subfound.store(true);
        lock_guard<mutex> lock(submu);
        cout<<"FOUND indices=";
        for(auto v:e.solution)cout<<v<<",";
        cout<<endl;
        ofstream out(subdir+"/solution.txt");for(auto v:e.solution)out<<v<<" ";out<<"\n";
      }else if(!substop.load() && !subfound.load()){
        ofstream out(f);out<<"nodes="<<e.nodes<<" leaves="<<e.leaves<<"\n";
        done++;
      }else{
        lock_guard<mutex> lock(submu);
        cout<<"INTERRUPTED prefix="<<prefixroot<<","<<second<<" nodes="<<e.nodes<<endl;
      }
    }
    if(!subfound.load() && done==(int)seconds.size()){
      ofstream rootdone(dir+"/root_"+to_string(prefixroot)+".done");
      rootdone<<"decomposed_prefixes="<<seconds.size()<<"\n";
    }
    cout<<"PREFIX_SUMMARY root="<<prefixroot<<" k="<<k<<" status="
        <<(subfound?"FOUND":done==(int)seconds.size()?"EXHAUSTED":"INCOMPLETE")
        <<" completed="<<done<<" total="<<seconds.size()
        <<" reused="<<reused<<" nodes_this_run="<<subnodes
        <<" elapsed="<<chrono::duration<double>(Clock::now()-begin).count()<<endl;
    return 0;
  }
  atomic<bool> stop{false}, found{false};
  atomic<uint64_t> totalnodes{0};
  atomic<int> completed{0}, reused{0}, started{0};
  mutex output;
  auto deadline=Clock::now()+chrono::duration_cast<Clock::duration>(chrono::duration<double>(seconds));
#pragma omp parallel for schedule(dynamic,1)
  for(int t=0;t<(int)pr.roots.size();t++){
    int root=pr.roots[pr.roots.size()-1-t];
    string file=dir+"/root_"+to_string(root)+".done";
    if(fs::exists(file)){completed++;reused++;continue;}
    if(stop.load()||found.load() || Clock::now()>deadline){stop.store(true);continue;}
    started++;
    Engine e(pr,k,root,stop,found,deadline);
    bool yes=e.solve();
    totalnodes+=e.nodes;
    if(yes){
      found.store(true);
      lock_guard<mutex> lock(output);
      cout<<"FOUND order="<<n<<" k="<<k<<" root="<<root<<" nodes="<<e.nodes<<" indices=";
      for(auto v:e.solution)cout<<v<<",";
      cout<<endl;
      ofstream out(dir+"/solution.txt");
      for(auto v:e.solution) out<<v<<" ";
      out<<"\n";
    } else if(!stop.load()&&!found.load()){
      ofstream out(file);out<<"nodes="<<e.nodes<<" leaves="<<e.leaves<<"\n";
      out.close();
      completed++;
      lock_guard<mutex> lock(output);
      cout<<"DONE root="<<root<<" nodes="<<e.nodes<<" completed="<<completed.load()<<"/"<<pr.roots.size()<<endl;
    }else{
      lock_guard<mutex> lock(output);
      cout<<"INTERRUPTED root="<<root<<" nodes="<<e.nodes<<" no_checkpoint_written"<<endl;
    }
  }
  double elapsed=chrono::duration<double>(Clock::now()-begin).count();
  cout<<"SUMMARY n="<<n<<" k="<<k<<" status="<< (found?"FOUND":completed==(int)pr.roots.size()?"EXHAUSTED":"INCOMPLETE")
      <<" completed_roots="<<completed<<" total_roots="<<pr.roots.size()<<" reused="<<reused
      <<" started="<<started<<" nodes_this_run="<<totalnodes<<" wall_seconds="<<elapsed<<endl;
}
