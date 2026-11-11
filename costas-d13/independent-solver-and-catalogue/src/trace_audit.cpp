// Fresh certificate interpreter for this audit; does not invoke the search.
// Board-mask graph, fixed 64-vertex subgraphs, complete sequential forest decode.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <zlib.h>
using namespace std;
using U=uint64_t;
void check(bool b,const char* msg) {if(!b)throw runtime_error(msg);}
struct Input {
  gzFile file;
  unsigned char buffer[1<<20];
  int at=0,size=0;
  uint64_t consumed=0;
  Input(const char* filename) {file=gzopen(filename,"rb");check(file,"open gzip");gzbuffer(file,1<<20);}
  int next() {
    if(at==size) {
      size=gzread(file,buffer,sizeof(buffer));at=0;
      check(size>=0,"gzip decompression failure");
      if(size==0) {int error;gzerror(file,&error);check(error==Z_OK||error==Z_STREAM_END,"gzip CRC/truncation error");return -1;}
    }
    ++consumed;return buffer[at++];
  }
  int byte() {int b=next();check(b>=0,"premature proof EOF");return b;}
  ~Input(){gzclose(file);}
};
struct Audit {
  int n,m,target,words;
  vector<vector<int>> a,key;
  vector<array<U,4>> boards;
  vector<vector<U>> edge;
  vector<int> rep;
  uint64_t nodes=0,edges=0;
  array<uint64_t,256> opcounts{};
  chrono::steady_clock::time_point start=chrono::steady_clock::now();
  Input& input;
  double elapsed(){return chrono::duration<double>(chrono::steady_clock::now()-start).count();}
  bool adjacent(int x,int y)const{return (edge[x][y/64]>>(y%64))&1;}
  Audit(const char* filename,int t,Input& in):target(t),input(in) {
    ifstream f(filename);check(bool(f>>n>>m),"catalogue header");
    check(n>=2&&n<=16&&m>0&&target>1&&target<=n,"parameters");
    a.assign(m,vector<int>(n));key.assign(m,vector<int>(2*n));boards.resize(m);
    map<vector<int>,int> lookup;
    for(int v=0;v<m;++v) {
      set<int> seen;
      for(int r=0;r<n;++r) {
        int c;check(bool(f>>c)&&c>=0&&c<n&&seen.insert(c).second,"permutation");
        a[v][r]=c;key[v][r]=c;key[v][n+c]=r;
        int cell=r*n+c;boards[v][cell/64]|=U(1)<<(cell%64);
      }
      check(lookup.emplace(a[v],v).second,"duplicate array");
      set<pair<int,int>> d;
      for(int r=0;r<n;++r) for(int s=r+1;s<n;++s)
        check(d.emplace(s-r,a[v][s]-a[v][r]).second,"non-Costas array");
    }
    string extra;check(!(f>>extra),"trailing catalogue data");
    rep.resize(m);
    for(int v=0;v<m;++v) {
      auto q=a[v];int best=v;
      for(int turn=0;turn<4;++turn) {
        vector<int> flipped(n),rotated(n);
        for(int r=0;r<n;++r){flipped[r]=n-1-q[r];rotated[q[r]]=n-1-r;}
        auto x=lookup.find(q),y=lookup.find(flipped);
        check(x!=lookup.end()&&y!=lookup.end(),"D4 closure");
        best=min(best,min(x->second,y->second));q=move(rotated);
      }
      rep[v]=best;
    }
    words=(m+63)/64;edge.assign(m,vector<U>(words));
    for(int x=0;x<m;++x) for(int y=0;y<x;++y) {
      bool conflict=false;
      for(int w=0;w<4;++w) if(boards[x][w]&boards[y][w]){conflict=true;break;}
      if(!conflict){edge[x][y/64]|=U(1)<<(y%64);edge[y][x/64]|=U(1)<<(x%64);++edges;}
    }
  }
  template<int W> struct Local {
    struct Mask {
      U words[W];
      bool any() const {for(U w:words)if(w)return true;return false;}
      int count() const {int c=0;for(U w:words)c+=__builtin_popcountll(w);return c;}
      int first() const {for(int w=0;w<W;++w)if(words[w])return w*64+__builtin_ctzll(words[w]);return -1;}
      int last() const {for(int w=W-1;w>=0;--w)if(words[w])return w*64+63-__builtin_clzll(words[w]);return -1;}
      void add(int v){words[v/64]|=U(1)<<(v%64);}
      void remove(int v){words[v/64]&=~(U(1)<<(v%64));}
      Mask intersection(const Mask& b)const{Mask c;for(int w=0;w<W;++w)c.words[w]=words[w]&b.words[w];return c;}
      void subtract(const Mask& b){for(int w=0;w<W;++w)words[w]&=~b.words[w];}
    };
    Audit& parent;
    int size;
    int ids[64*W];
    Mask neighbors[64*W],cell[32][16];
    bool have_neighbor[64*W]{},have_row[32]{};
    Local(Audit& p,const vector<int>& vertices):parent(p),size(vertices.size()) {
      copy(vertices.begin(),vertices.end(),ids);
    }
    const Mask& neighborhood(int v) {
      if(!have_neighbor[v]) {
        neighbors[v]=Mask{};
        for(int y=0;y<size;++y)if(parent.adjacent(ids[v],ids[y]))neighbors[v].add(y);
        have_neighbor[v]=true;
      }
      return neighbors[v];
    }
    void prepare_row(int r) {
      if(have_row[r])return;
      for(int c=0;c<parent.n;++c)cell[r][c]=Mask{};
      for(int x=0;x<size;++x)cell[r][parent.key[ids[x]][r]].add(x);
      have_row[r]=true;
    }
    void decode(Mask p,int need) {
      check(need>0,"target reached inside negative proof");++parent.nodes;
      int op=parent.input.byte();++parent.opcounts[op];
      int count=p.count();
      if(op==253){check(count<need,"false cardinality leaf");return;}
      Mask classes[64*W];int colours=0;
      if(op<2*parent.n) {
        prepare_row(op);
        struct Group{Mask mask;int count,first;};Group groups[16];
        for(int c=0;c<parent.n;++c){Mask q=p.intersection(cell[op][c]);if(q.any())groups[colours++]={q,q.count(),q.first()};}
        sort(groups,groups+colours,[](const Group& x,const Group& y){return x.count!=y.count?x.count>y.count:x.first<y.first;});
        for(int c=0;c<colours;++c)classes[c]=groups[c].mask;
      } else {
        check(op==254,"unsupported/invalid opcode");
        Mask left=p;
        while(left.any()) {
          Mask available=left,group{};
          while(available.any()) {
            int v=available.first();
            left.remove(v);group.add(v);available.remove(v);available.subtract(neighborhood(v));
          }
          classes[colours++]=group;
        }
      }
      // Every completion has a unique greatest member in this class ordering.
      for(int c=colours-1;c>=need-1;--c) {
        Mask q=classes[c];
        while(q.any()) {
          int v=q.last();q.remove(v);
          check(need>1,"proof attempts to refute an existing clique");
          decode(p.intersection(neighborhood(v)),need-1);p.remove(v);
        }
      }
    }
  };
  template<int W> void local_decode(const vector<int>& p,int need) {
    // Allocation once per local subtree; adjacency rows and partitions are lazy.
    auto sub=new Local<W>(*this,p);
    typename Local<W>::Mask mask{};
    for(int v=0;v<int(p.size());++v)mask.add(v);
    sub->decode(mask,need);delete sub;
  }
  // Stack vectors: small nodes use no projected graph or heap allocation.
  void stack_decode(const int* vertices,int length,int need) {
    check(need>0,"target reached inside negative proof");++nodes;
    int op=input.byte();++opcounts[op];
    if(op==253){check(length<need,"false cardinality leaf");return;}
    uint8_t members[128][128];uint16_t counts[128]{};
    int ordering[128],nc=0;
    if(op<2*n) {
      for(int i=0;i<length;++i){int c=key[vertices[i]][op];members[c][counts[c]++]=i;}
      for(int c=0;c<n;++c)if(counts[c])ordering[nc++]=c;
      sort(ordering,ordering+nc,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:members[x][0]<members[y][0];});
    } else {
      check(op==254,"unsupported/invalid opcode");
      for(int i=0;i<length;++i) {
        int colour=0;const U* row=edge[vertices[i]].data();
        for(;colour<nc;++colour) {
          bool fits=true;
          for(int j=0;j<counts[colour];++j) {
            int v=vertices[members[colour][j]];
            if((row[v/64]>>(v%64))&1){fits=false;break;}
          }
          if(fits)break;
        }
        if(colour==nc){ordering[nc]=nc;++nc;}
        members[colour][counts[colour]++]=i;
      }
    }
    if(nc<need)return;
    bool active[128];fill(active,active+length,true);int child[128];
    for(int colour=nc-1;colour>=need-1;--colour) {
      int cls=ordering[colour];
      for(int j=int(counts[cls])-1;j>=0;--j) {
        check(need>1,"proof attempts to refute an existing clique");
        int v=members[cls][j],len=0;const U* row=edge[vertices[v]].data();
        for(int u=0;u<length;++u)if(active[u]&&((row[vertices[u]/64]>>(vertices[u]%64))&1))child[len++]=vertices[u];
        stack_decode(child,len,need-1);active[v]=false;
      }
    }
  }
  void decode(const vector<int>& p,int need) {
    if(p.size()<=128){stack_decode(p.data(),p.size(),need);return;}
    check(need>0,"target reached inside negative proof");++nodes;
    int op=input.byte();++opcounts[op];
    if(op==253){check(int(p.size())<need,"false cardinality leaf");return;}
    vector<vector<int>> classes;
    if(op<2*n) {
      classes.resize(n);for(int v:p)classes[key[v][op]].push_back(v);
      classes.erase(remove_if(classes.begin(),classes.end(),[](const auto& c){return c.empty();}),classes.end());
      sort(classes.begin(),classes.end(),[](const auto& x,const auto& y){return x.size()!=y.size()?x.size()>y.size():x.front()<y.front();});
    } else {
      check(op==254,"unsupported/invalid opcode");
      for(int v:p) {
        size_t c=0;
        for(;c<classes.size();++c) {
          bool independent=true;
          for(int u:classes[c])if(adjacent(u,v)){independent=false;break;}
          if(independent)break;
        }
        if(c==classes.size()) classes.emplace_back();
        classes[c].push_back(v);
      }
    }
    vector<int> active=p;
    for(int c=int(classes.size())-1;c>=need-1;--c)for(auto it=classes[c].rbegin();it!=classes[c].rend();++it) {
      int v=*it;check(need>1,"proof attempts to refute an existing clique");
      vector<int> child;for(int u:active)if(adjacent(u,v))child.push_back(u);
      decode(child,need-1);
      auto at=lower_bound(active.begin(),active.end(),v);check(at!=active.end()&&*at==v,"branch vertex absent");active.erase(at);
    }
  }
  void run(const string& prefix) {
    ofstream log(prefix+".roots.jsonl");check(bool(log),"root log open");int roots=0;
    for(int i=0;i<m;++i)if(rep[i]==i) {
      vector<int> p;for(int j=i+1;j<m;++j)if(rep[j]>=i&&adjacent(i,j))p.push_back(j);
      uint64_t before=nodes;double t=elapsed();decode(p,target-1);
      log<<"{\"ordinal\":"<<roots<<",\"vertex\":"<<i<<",\"nodes\":"<<nodes-before<<",\"seconds\":"<<elapsed()-t<<"}\n";log.flush();
      ++roots;if(roots%10==0)cerr<<"roots="<<roots<<" nodes="<<nodes<<" seconds="<<elapsed()<<"\n";
    }
    for(char c:string("ENDPROOF"))check(input.byte()==c,"completion marker");
    check(input.next()==-1,"trailing decoded proof bytes");
    ofstream out(prefix+".json");
    out<<"{\"verified\":true,\"n\":"<<n<<",\"target\":"<<target<<",\"vertices\":"<<m<<",\"edges\":"<<edges<<",\"roots\":"<<roots<<",\"nodes\":"<<nodes<<",\"bytes\":"<<input.consumed<<",\"seconds\":"<<elapsed()<<",\"opcounts\":{";
    bool sep=false;for(int op=0;op<256;++op)if(opcounts[op]){out<<(sep?",":"")<<'\"'<<op<<"\":"<<opcounts[op];sep=true;}out<<"}}\n";
  }
};
int main(int argc,char**argv){try{check(argc==5,"usage: trace_audit catalogue proof.gz target prefix");Input in(argv[2]);Audit a(argv[1],stoi(argv[3]),in);a.run(argv[4]);}catch(const exception& e){cerr<<"REJECT: "<<e.what()<<'\n';return 1;}}
