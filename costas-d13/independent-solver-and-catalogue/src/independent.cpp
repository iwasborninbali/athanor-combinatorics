// Independent exact clique decision. Written for this adversarial audit.
// No D4 operations, orbit representatives, proof advice, or inherited code.
// Roots are ALL catalogue indices, with only j > root allowed.
#include <algorithm>
#include <array>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using U = uint64_t;
static volatile sig_atomic_t interrupted = 0;
static void stop_handler(int) { interrupted = 1; }
struct Solver {
  int n, m, k, words;
  vector<vector<int>> a, key;
  vector<vector<U>> g;
  vector<int> path, solution;
  uint64_t nodes = 0, edges = 0, cardinality = 0, colours = 0;
  bool stopped = false, greedy_only = false;
  double seconds_limit;
  chrono::steady_clock::time_point start;
  double elapsed() const {
    return chrono::duration<double>(chrono::steady_clock::now()-start).count();
  }
  bool tick() {
    ++nodes;
    if ((nodes & 65535) == 0 && (interrupted || elapsed() >= seconds_limit)) stopped = true;
    return !stopped;
  }
  bool adjacent(int x, int y) const { return (g[x][y/64] >> (y%64)) & 1; }
  explicit Solver(const string& filename, int target, double limit): k(target), seconds_limit(limit) {
    ifstream f(filename);
    if (!(f >> n >> m) || n < 2 || n > 30 || m < 1) throw runtime_error("bad header");
    a.assign(m, vector<int>(n)); key.assign(m, vector<int>(2*n));
    for(int v=0; v<m; ++v) {
      unsigned seen=0;
      for(int r=0; r<n; ++r) {
        int c; if(!(f>>c) || c<0 || c>=n || (seen & (1U<<c))) throw runtime_error("bad permutation");
        seen |= 1U<<c; a[v][r]=c; key[v][r]=c; key[v][n+c]=r;
      }
      for(int d=1;d<n;++d) {
        U seen_diff=0;
        for(int r=0;r+d<n;++r) {
          U b=U(1) << (a[v][r+d]-a[v][r]+n);
          if(seen_diff & b) throw runtime_error("non-Costas row");
          seen_diff |= b;
        }
      }
    }
    string extra; if(f>>extra) throw runtime_error("extra input");
    words=(m+63)/64; g.assign(m, vector<U>(words));
    // Direct pairwise definition, without cell-incidence complementation.
    for(int x=0;x<m;++x) for(int y=0;y<x;++y) {
      bool disjoint=true;
      for(int r=0;r<n;++r) if(a[x][r]==a[y][r]) { disjoint=false; break; }
      if(disjoint) { g[x][y/64]|=U(1)<<(y%64); g[y][x/64]|=U(1)<<(x%64); ++edges; }
    }
    start=chrono::steady_clock::now();
  }
  // A projected graph with lazy adjacency, created at <=512 candidates.
  template<int W> struct Small {
    struct Mask {
      U words[W];
      bool any()const{for(U w:words)if(w)return true;return false;}
      int count()const{int z=0;for(U w:words)z+=__builtin_popcountll(w);return z;}
      int first()const{for(int w=0;w<W;++w)if(words[w])return w*64+__builtin_ctzll(words[w]);return -1;}
      int last()const{for(int w=W-1;w>=0;--w)if(words[w])return w*64+63-__builtin_clzll(words[w]);return -1;}
      void set(int v){words[v/64]|=U(1)<<(v%64);}
      void erase(int v){words[v/64]&=~(U(1)<<(v%64));}
      Mask both(const Mask& b)const{Mask z;for(int w=0;w<W;++w)z.words[w]=words[w]&b.words[w];return z;}
      void subtract(const Mask& b){for(int w=0;w<W;++w)words[w]&=~b.words[w];}
    };
    Solver& s;
    int size;
    int id[64*W];
    Mask edge[64*W],cell[60][30];
    bool edge_ready[64*W]{},row_ready[60]{};
    Small(Solver& parent, const vector<int>& p):s(parent),size(p.size()) {
      copy(p.begin(),p.end(),id);
    }
    const Mask& neighbors(int v) {
      if(!edge_ready[v]) {
        edge[v]=Mask{};
        for(int y=0;y<size;++y)if(s.adjacent(id[v],id[y]))edge[v].set(y);
        edge_ready[v]=true;
      }
      return edge[v];
    }
    void row(int r) {
      if(row_ready[r])return;
      for(int c=0;c<s.n;++c)cell[r][c]=Mask{};
      for(int v=0;v<size;++v)cell[r][s.key[id[v]][r]].set(v);
      row_ready[r]=true;
    }
    bool visit(Mask p, int need) {
      if(!s.tick()) return false;
      if(p.count()<need) { ++s.cardinality; return false; }
      if(need==1) { s.solution=s.path; s.solution.push_back(id[p.first()]); return true; }
      Mask groups[64*W]; int ng=0, bestscore=100000, chosen=-1;
      Mask left=p;
      while(left.any()) {
        Mask available=left, cls{};
        while(available.any()) {
          int x=available.first();
          cls.set(x); left.erase(x); available.erase(x);available.subtract(neighbors(x));
        }
        groups[ng++]=cls;
      }
      if(ng<need) { ++s.colours; return false; }
      // Fixed cell-label ties deliberately differ from the reviewed implementation.
      if(!s.greedy_only) for(int r=0;r<2*s.n;++r) {
        row(r);
        int counts[30],nc=0;
        for(int c=0;c<s.n;++c) {Mask q=p.both(cell[r][c]);if(q.any()) counts[nc++]=q.count();}
        if(nc<need) { ++s.colours; return false; }
        sort(counts,counts+nc);
        int score=accumulate(counts,counts+nc-need+1,0);
        if(score<bestscore) { bestscore=score; chosen=r; }
      }
      int gs=0;
      for(int c=need-1;c<ng;++c) gs+=groups[c].count();
      if(chosen>=0 && bestscore<=gs) {
        vector<pair<int,int>> sizes;
        for(int c=0;c<s.n;++c) {Mask q=p.both(cell[chosen][c]);if(q.any())sizes.emplace_back(-q.count(),c);}
        sort(sizes.begin(),sizes.end()); ng=0;
        for(auto sc:sizes) groups[ng++]=p.both(cell[chosen][sc.second]);
      }
      for(int c=ng-1;c>=need-1;--c) {
        Mask cls=groups[c];
        while(cls.any()) {
          // Largest local index first, a deterministic reverse prefix traversal.
          int x=cls.last(); cls.erase(x);
          s.path.push_back(id[x]);
          if(visit(p.both(neighbors(x)),need-1)) return true;
          s.path.pop_back();
          if(s.stopped) return false;
          p.erase(x);
        }
      }
      return false;
    }
  };
  template<int W>bool small_visit(const vector<int>& p,int need) {
    auto sub=new Small<W>(*this,p);
    typename Small<W>::Mask mask{};
    for(int v=0;v<int(p.size());++v)mask.set(v);
    bool sat=sub->visit(mask,need);delete sub;return sat;
  }
  bool visit(const vector<int>& p, int need) {
    if(p.size()<=64)return small_visit<1>(p,need);
    if(p.size()<=128)return small_visit<2>(p,need);
    if(p.size()<=256)return small_visit<4>(p,need);
    if(p.size()<=512)return small_visit<8>(p,need);
    if(!tick()) return false;
    if(int(p.size())<need) { ++cardinality; return false; }
    if(need==1) { solution=path; solution.push_back(p.front()); return true; }
    vector<vector<int>> classes;
    int selected=-1, bestscore=100000000;
    if(!greedy_only) for(int r=0;r<2*n;++r) {
      vector<int> counts(n);
      for(int v:p) ++counts[key[v][r]];
      counts.erase(remove(counts.begin(),counts.end(),0),counts.end());
      if(int(counts.size())<need) { ++colours; return false; }
      sort(counts.begin(),counts.end());
      int score=accumulate(counts.begin(),counts.end()-need+1,0);
      if(score<bestscore) { bestscore=score; selected=r; }
    }
    // First-fit proper colouring, with direct tests against each class member.
    for(int v:p) {
      size_t c=0;
      for(;c<classes.size();++c) {
        bool fits=true;
        for(int u:classes[c]) if(adjacent(u,v)) { fits=false; break; }
        if(fits) break;
      }
      if(c==classes.size()) classes.emplace_back();
      classes[c].push_back(v);
    }
    if(int(classes.size())<need) { ++colours; return false; }
    int gs=0; for(size_t c=need-1;c<classes.size();++c) gs+=classes[c].size();
    if(selected>=0 && bestscore<=gs) {
      vector<vector<int>> blocks(n);
      for(int v:p) blocks[key[v][selected]].push_back(v);
      vector<int> order(n); iota(order.begin(),order.end(),0);
      stable_sort(order.begin(),order.end(),[&](int x,int y){return blocks[x].size()>blocks[y].size();});
      classes.clear(); for(int c:order) if(!blocks[c].empty()) classes.push_back(move(blocks[c]));
    }
    // No global candidate bitset is passed between levels: filtered vectors.
    vector<int> active=p;
    for(int c=int(classes.size())-1;c>=need-1;--c) {
      for(auto it=classes[c].rbegin();it!=classes[c].rend();++it) {
        int v=*it;
        vector<int> child; child.reserve(active.size()/2);
        for(int u:active) if(adjacent(u,v)) child.push_back(u);
        path.push_back(v);
        if(visit(child,need-1)) return true;
        path.pop_back(); if(stopped) return false;
        auto at=lower_bound(active.begin(),active.end(),v);
        if(at==active.end() || *at!=v) throw runtime_error("missing active vertex");
        active.erase(at);
      }
    }
    return false;
  }
};
int main(int argc,char**argv) {
  try {
    if(argc<6) { cerr<<"usage: independent catalogue target seconds prefix root_begin [root_end [mod residue [greedy_only]]]\n"; return 2; }
    signal(SIGTERM,stop_handler); signal(SIGINT,stop_handler);
    Solver s(argv[1],stoi(argv[2]),stod(argv[3]));
    string prefix=argv[4]; int begin=stoi(argv[5]),end=argc>6?stoi(argv[6]):s.m;
    int mod=argc>7?stoi(argv[7]):1,res=argc>8?stoi(argv[8]):0;
    if(argc>9) s.greedy_only=stoi(argv[9]);
    if(begin<0||end>s.m||begin>end||mod<1||res<0||res>=mod) throw runtime_error("bad scope");
    ofstream roots(prefix+".roots.jsonl"); if(!roots) throw runtime_error("cannot open log");
    bool sat=false; int completed=0;
    for(int i=begin;i<end;++i) if(i%mod==res) {
      if(interrupted || s.elapsed()>=s.seconds_limit) {s.stopped=true;break;}
      vector<int> p; for(int j=i+1;j<s.m;++j) if(s.adjacent(i,j)) p.push_back(j);
      s.path={i}; auto before=s.nodes; double t=s.elapsed();
      sat=s.visit(p,s.k-1);
      roots<<"{\"root\":"<<i<<",\"nodes\":"<<s.nodes-before<<",\"seconds\":"<<s.elapsed()-t<<",\"complete\":"<<(!sat&&!s.stopped?"true":"false")<<"}\n"; roots.flush();
      cerr<<"root="<<i<<" nodes="<<s.nodes-before<<" total="<<s.nodes<<" seconds="<<s.elapsed()<<"\n";
      if(!sat&&!s.stopped) ++completed;
      if(sat||s.stopped) break;
    }
    string status=sat?"SAT":s.stopped?"INCOMPLETE":"EXHAUSTED_SCOPE";
    ofstream out(prefix+".json");
    out<<"{\"status\":\""<<status<<"\",\"n\":"<<s.n<<",\"m\":"<<s.m<<",\"target\":"<<s.k<<",\"edges\":"<<s.edges<<",\"nodes\":"<<s.nodes<<",\"seconds\":"<<s.elapsed()<<",\"begin\":"<<begin<<",\"end\":"<<end<<",\"mod\":"<<mod<<",\"residue\":"<<res<<",\"completed_roots\":"<<completed<<",\"D4\":false,\"greedy_only\":"<<(s.greedy_only?"true":"false")<<",\"cardinality_cuts\":"<<s.cardinality<<",\"colour_cuts\":"<<s.colours<<",\"witness\":[";
    for(size_t i=0;i<s.solution.size();++i) out<<(i?",":"")<<s.solution[i];
    out<<"]}\n";
    cout<<status<<" nodes="<<s.nodes<<" seconds="<<s.elapsed()<<"\n";
    return s.stopped?3:0;
  } catch(const exception& e) {cerr<<e.what()<<"\n";return 2;}
}
