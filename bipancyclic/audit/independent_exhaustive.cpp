// Independent exhaustive audit. No submitted code, patterns, or certificates.
// Rotations only: mirror images are deliberately retained.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <functional>
#include <iostream>
#include <numeric>
#include <set>
#include <utility>
#include <vector>
using namespace std;
using Edge = pair<int,int>;
using Pattern = vector<Edge>;

struct Cycle { unsigned arcs; int chords; };
struct Expr { unsigned low, high; int constant; };

bool rotation_minimal(const Pattern& p, int m) {
    for (int r=1; r<m; ++r) {
        Pattern q;
        for (auto [u,v]:p) {
            u=(u+r)%m; v=(v+r)%m;
            if(u>v) swap(u,v);
            q.push_back({u,v});
        }
        sort(q.begin(),q.end());
        if(q<p) return false;
    }
    return true;
}

// Enumerate ALL edge subsets, select connected nonempty 2-regular subgraphs.
// This supports parallel arc/chord edges, including m=2 parallel ring arcs.
vector<Cycle> kernel_cycles(int m, const Pattern& chords) {
    Pattern edges;
    for(int i=0;i<m;++i) edges.push_back({i,(i+1)%m});
    edges.insert(edges.end(),chords.begin(),chords.end());
    vector<Cycle> out;
    for(unsigned s=1;s<(1u<<edges.size());++s) {
        int deg[8]={}, parent[8];
        iota(parent,parent+m,0);
        auto find=[&](int a){while(parent[a]!=a) a=parent[a]; return a;};
        bool good=true;
        for(int i=0;i<(int)edges.size();++i) if((s>>i)&1) {
            auto [u,v]=edges[i];
            if(++deg[u]>2 || ++deg[v]>2) {good=false;break;}
            parent[find(u)]=find(v);
        }
        if(!good) continue;
        int component=-1;
        for(int i=0;i<m;++i) if(deg[i]) {
            if(deg[i]!=2) {good=false;break;}
            if(component<0) component=find(i);
            if(find(i)!=component) {good=false;break;}
        }
        if(good) out.push_back({s&((1u<<m)-1),__builtin_popcount(s>>m)});
    }
    return out;
}

struct Run {
    int n,k,m;
    uint64_t patterns=0, cases=0, leaves=0, solutions=0;
    uint64_t rotation_patterns=0, all_patterns=0;
    uint64_t discarded_cycle_count=0;
    vector<Expr> expr;
    int x[8]={}, base[8]={};
    Pattern p;
    bool stop_at_first=false;
    bool quotient_rotations=true;
    uint64_t target;

    // No interval pruning. Every integer composition reaches this leaf.
    void inspect() {
        ++leaves;
        int lo[16]={},hi[16]={};
        for(int s=1;s<16;++s) {
            unsigned bit=__builtin_ctz((unsigned)s);
            lo[s]=lo[s&(s-1)]+x[bit];
            hi[s]=hi[s&(s-1)]+x[bit+4];
        }
        uint64_t seen=0;
        for(const auto& e:expr)
            seen |= 1ull<<(e.constant+lo[e.low]+hi[e.high]);
        if((seen&target)==target) {
            ++solutions;
            cout << "{\"kind\":\"solution\",\"N\":"<<n<<",\"k\":"<<k<<",\"arcs\":[";
            for(int i=0;i<m;++i) cout<<(i?",":"")<<base[i]+2*x[i];
            cout<<"],\"endpoint_chords\":[";
            for(int i=0;i<k;++i) cout<<(i?",":"")<<"["<<p[i].first<<","<<p[i].second<<"]";
            cout<<"]}"<<endl;
        }
    }
    bool compositions(int pos,int remaining) {
        if(pos==m-1) {x[pos]=remaining;inspect();return solutions && stop_at_first;}
        for(int v=0;v<=remaining;++v) {
            x[pos]=v;
            if(compositions(pos+1,remaining-v)) return true;
        }
        return false;
    }
    bool examine(const vector<Cycle>& cyc) {
        ++patterns;
        if((int)cyc.size()<n/2-1) {++discarded_cycle_count;return false;}
        // Enumerate endpoint colors with endpoint zero fixed to zero.
        for(unsigned color=0;color<(1u<<m);color+=2) {
            bool good=true;
            for(auto [u,v]:p) if(((color>>u)&1)==((color>>v)&1)) {good=false;break;}
            if(!good) continue;
            for(int i=0;i<m;++i)
                base[i]=(((color>>i)^(color>>((i+1)%m)))&1)?1:2;
            for(auto [u,v]:p) {
                if((u+1)%m==v) base[u]=3;
                if((v+1)%m==u) base[v]=3;
            }
            int bsum=accumulate(base,base+m,0);
            if(bsum>n || (n-bsum)%2) continue;
            ++cases;
            expr.clear();
            for(auto c:cyc) {
                int length=c.chords;
                for(int i=0;i<m;++i) if((c.arcs>>i)&1) length+=base[i];
                if(length%2) {cerr<<"PARITY FAILURE"<<endl;exit(2);}
                expr.push_back({c.arcs&15,c.arcs>>4,length/2});
            }
            fill(x,x+8,0);
            if(compositions(0,(n-bsum)/2)) return true;
        }
        return false;
    }
    bool generate(int next, int left, Pattern& chosen, const Pattern& pairs) {
        if(left==0) {
            unsigned used=0;
            for(auto [u,v]:chosen) used|=(1u<<u)|(1u<<v);
            if(used!=((1u<<m)-1)) return false;
            ++all_patterns;
            if(quotient_rotations && !rotation_minimal(chosen,m)) return false;
            ++rotation_patterns;
            p=chosen;
            return examine(kernel_cycles(m,p));
        }
        for(int i=next;i<=(int)pairs.size()-left;++i) {
            chosen.push_back(pairs[i]);
            if(generate(i+1,left-1,chosen,pairs)) return true;
            chosen.pop_back();
        }
        return false;
    }
    void run() {
        auto start=clock();
        target=((1ull<<(n/2+1))-1)&~3ull;
        for(m=2;m<=2*k;++m) {
            Pattern pairs,chosen;
            for(int u=0;u<m;++u) for(int v=u+1;v<m;++v) pairs.push_back({u,v});
            if(generate(0,k,chosen,pairs)) break;
        }
        cout<<"{\"kind\":\"exhaustion\",\"N\":"<<n<<",\"k\":"<<k
            <<",\"all_labeled_patterns\":"<<all_patterns<<",\"selected_patterns\":"<<rotation_patterns
            <<",\"symmetry\":\""<<(quotient_rotations?"rotations":"none")<<"\""
            <<",\"cycle_count_pruned_patterns\":"<<discarded_cycle_count
            <<",\"admissible_cases\":"<<cases<<",\"compositions_evaluated\":"<<leaves
            <<",\"solutions\":"<<solutions<<",\"complete\":"<<(!stop_at_first?"true":"false")
            <<",\"cpu_seconds\":"<<double(clock()-start)/CLOCKS_PER_SEC<<"}"<<endl;
    }
};

void census(int k) {
    for(int m=2;m<=2*k;++m) {
        Pattern pairs,p;
        for(int u=0;u<m;++u) for(int v=u+1;v<m;++v) pairs.push_back({u,v});
        uint64_t total=0,rot=0; int maxcyc=0;
        function<void(int,int)> rec=[&](int start,int left) {
            if(left==0) {
                unsigned used=0;
                for(auto [u,v]:p) used|=(1u<<u)|(1u<<v);
                if(used!=((1u<<m)-1)) return;
                ++total;
                if(rotation_minimal(p,m)) {++rot;maxcyc=max(maxcyc,(int)kernel_cycles(m,p).size());}
                return;
            }
            for(int i=start;i<=(int)pairs.size()-left;++i) {
                p.push_back(pairs[i]);rec(i+1,left-1);p.pop_back();
            }
        };
        rec(0,k);
        cout<<"{\"kind\":\"census\",\"k\":"<<k<<",\"m\":"<<m
            <<",\"labeled\":"<<total<<",\"rotations\":"<<rot<<",\"max_cycles\":"<<maxcyc<<"}"<<endl;
    }
}

int main(int argc,char**argv) {
    if(argc>=5 && string(argv[1])=="spectrum") {
        int n=stoi(argv[2]);Pattern chords;vector<int> endpoints;
        for(int i=3;i+1<argc;i+=2) {
            int u=stoi(argv[i]),v=stoi(argv[i+1]);
            chords.push_back({u,v});endpoints.push_back(u);endpoints.push_back(v);
        }
        sort(endpoints.begin(),endpoints.end());
        endpoints.erase(unique(endpoints.begin(),endpoints.end()),endpoints.end());
        int m=endpoints.size();
        if(m>8) return 2;
        for(auto& [u,v]:chords) {
            u=lower_bound(endpoints.begin(),endpoints.end(),u)-endpoints.begin();
            v=lower_bound(endpoints.begin(),endpoints.end(),v)-endpoints.begin();
        }
        int hist[65]={};
        for(auto c:kernel_cycles(m,chords)) {
            int length=c.chords;
            for(int i=0;i<m;++i) if((c.arcs>>i)&1)
                length+=(endpoints[(i+1)%m]-endpoints[i]+n)%n;
            ++hist[length];
        }
        cout<<"{";
        bool comma=false;
        for(int i=0;i<=n;++i) if(hist[i]) {cout<<(comma?",":"")<<"\""<<i<<"\":"<<hist[i];comma=true;}
        cout<<"}"<<endl;return 0;
    }
    if(argc==3 && string(argv[1])=="census") {census(stoi(argv[2]));return 0;}
    if(argc<3) {cerr<<"usage: program k N [first|all] | census k\n";return 2;}
    Run r; r.k=stoi(argv[1]);r.n=stoi(argv[2]);
    r.stop_at_first=argc>3 && string(argv[3])=="first";
    r.quotient_rotations=!(argc>3 && string(argv[3])=="all");
    r.run();
}
