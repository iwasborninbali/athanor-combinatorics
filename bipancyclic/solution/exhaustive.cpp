// Exhaustive positive-arc search. Its binary exclusion trees are checked by
// check_exclusions.py, which independently generates patterns and simple cycles.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>
#include <sys/statvfs.h>
using namespace std;

struct Cycle { int mask, chords, chord_mask; };
struct Pattern { int id, m, k; vector<pair<int,int>> pairs; vector<Cycle> cycles; };
struct Case { const Pattern* p; int color, S; vector<int> base; };
uint64_t binom(int n, int k) {
    if(k<0 || k>n) return 0;
    uint64_t z=1;
    for(int i=1;i<=k;i++) z=z*(n-k+i)/i;
    return z;
}
void put16(int z) { putchar(z&255); putchar((z>>8)&255); }
bool space_ok() {
    struct statvfs s;
    return statvfs(".",&s)==0 && (uint64_t)s.f_bavail*s.f_frsize >= 3ULL*1024*1024*1024;
}

struct Search {
    int N,m,q;
    const Case& ca;
    uint64_t target, nodes=0, represented=0;
    array<int,32> value{}, cmask{};
    array<int,8> x{};
    array<array<int,32>,9> kind{};
    array<vector<int>,8> affects;
    bool proof;
    Search(int n,const Case& c,bool pr):N(n),m(c.p->m),q(c.p->cycles.size()),ca(c),proof(pr) {
        target=((1ULL<<(N/2+1))-1) ^ 3ULL;
        for(int j=0;j<q;j++) {
            cmask[j]=ca.p->cycles[j].mask;
            int z=ca.p->cycles[j].chords;
            for(int i=0;i<m;i++) if(cmask[j]>>i&1) {z+=ca.base[i];affects[i].push_back(j);}
            if(z%2) {cerr<<"bad parity\n";exit(3);}
            value[j]=z/2;
            for(int d=0;d<=m;d++) {
                int rem=((1<<m)-1)^((1<<d)-1), a=cmask[j]&rem;
                kind[d][j]=(a==0 ? 0 : a==rem ? 1 : 2);
            }
        }
    }
    bool visit(int d,int r) {
        nodes++;
        uint64_t covered=0;
        for(int j=0;j<q;j++) {
            int ty=kind[d][j],lo=value[j]+(ty==1?r:0),hi=lo+(ty==2?r:0);
            lo=max(2,lo);hi=min(N/2,hi);
            if(lo<=hi) covered|=((1ULL<<(hi+1))-1)^((1ULL<<lo)-1);
        }
        uint64_t missing=target&~covered;
        if(missing) {
            int t=__builtin_ctzll(missing);
            if(proof) putchar(t);
            represented+=binom(r+m-d-1,m-d-1);
            return false;
        }
        if(m-d==1) {x[d]=r;return true;}
        if(proof) putchar(0);
        for(int v=0;v<=r;v++) {
            x[d]=v;
            if(visit(d+1,r-v)) return true;
            if(v<r) for(int j:affects[d]) value[j]++;
        }
        for(int j:affects[d]) value[j]-=r;
        return false;
    }
};

int main(int argc,char**argv) {
    if(argc<3) {cerr<<"usage: exhaustive PATTERNS.txt N [--proof]\n";return 2;}
    int N=stoi(argv[2]);bool proof=argc>3 && string(argv[3])=="--proof";
    if(N<4 || N>64 || N%2) return 2;
    if(!space_ok()) {cerr<<"less than 3 GiB free; stopped\n";return 4;}
    ifstream in(argv[1]);int np;in>>np;
    vector<Pattern> ps(np);
    for(auto&p:ps) {
        int q;in>>p.id>>p.m>>q>>p.k;
        for(int i=0;i<p.k;i++){int a,b;in>>a>>b;p.pairs.emplace_back(a,b);}
        for(int i=0;i<q;i++){Cycle c;in>>c.mask>>c.chords>>c.chord_mask;p.cycles.push_back(c);}
    }
    if(!in) {cerr<<"bad input\n";return 2;}
    vector<Case> cases;
    int count_skipped=0,parities=0;
    for(const auto&p:ps) {
        if((int)p.cycles.size()<N/2-1) {count_skipped++;continue;}
        for(int col=0;col<(1<<(p.m-1));col++) {
            auto color=[&](int v){return v==0?0:((col>>(v-1))&1);};
            bool valid=true;
            for(auto [a,b]:p.pairs) if(color(a)==color(b)) valid=false;
            if(!valid) continue;
            parities++;
            vector<int> base(p.m);
            for(int i=0;i<p.m;i++) base[i]=(color(i)!=color((i+1)%p.m)?1:2);
            for(auto [a,b]:p.pairs) {
                if((a+1)%p.m==b) base[a]=3;
                if((b+1)%p.m==a) base[b]=3;
            }
            int left=N-accumulate(base.begin(),base.end(),0);
            if(left>=0 && left%2==0) cases.push_back({&p,col,left/2,base});
        }
    }
    cerr<<"{\"type\":\"start\",\"N\":"<<N<<",\"patterns\":"<<np<<",\"count_skipped\":"<<count_skipped<<",\"cases\":"<<cases.size()<<"}\n";
    if(proof) {fwrite("BPC1",1,4,stdout);putchar(N);putchar(ps[0].k);put16(cases.size());}
    auto begin=chrono::steady_clock::now();uint64_t totalnodes=0,totalassign=0;
    for(const auto&ca:cases) {
        if(!space_ok()) {cerr<<"less than 3 GiB free; stopped\n";return 4;}
        if(proof) {putchar(ca.p->id);putchar(ca.color);}
        Search s(N,ca,proof);bool found=s.visit(0,ca.S);
        uint64_t expected=binom(ca.S+ca.p->m-1,ca.p->m-1);
        double sec=chrono::duration<double>(chrono::steady_clock::now()-begin).count();
        cerr<<"{\"type\":\"case\",\"N\":"<<N<<",\"pattern\":"<<ca.p->id<<",\"color\":"<<ca.color<<",\"S\":"<<ca.S<<",\"assignments\":"<<expected<<",\"represented\":"<<s.represented<<",\"nodes\":"<<s.nodes<<",\"found\":"<<(found?"true":"false")<<",\"elapsed\":"<<sec<<"}\n";
        if(found) {
            vector<int> a(ca.p->m),pos(ca.p->m);int at=0;
            for(int i=0;i<ca.p->m;i++){pos[i]=at;a[i]=ca.base[i]+2*s.x[i];at+=a[i];}
            cerr<<"{\"type\":\"witness\",\"N\":"<<N<<",\"arcs\":[";
            for(int i=0;i<ca.p->m;i++)cerr<<(i?",":"")<<a[i];
            cerr<<"],\"chords\":[";
            for(int i=0;i<ca.p->k;i++) {auto[u,v]=ca.p->pairs[i];cerr<<(i?",":"")<<"["<<pos[u]<<","<<pos[v]<<"]";}
            cerr<<"]}\n";
            return 10;
        }
        if(s.represented!=expected) {cerr<<"accounting failure\n";return 3;}
        totalnodes+=s.nodes;totalassign+=expected;
    }
    double sec=chrono::duration<double>(chrono::steady_clock::now()-begin).count();
    cerr<<"{\"type\":\"UNSAT\",\"N\":"<<N<<",\"cases\":"<<cases.size()<<",\"assignments\":"<<totalassign<<",\"nodes\":"<<totalnodes<<",\"seconds\":"<<sec<<"}\n";
    return 0;
}
