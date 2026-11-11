// One-thread tabu/min-conflicts discovery search; no negative claims.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){
 if(argc<6){cerr<<"usage: local_pack catalogue k seconds seed output-prefix\n";return 2;}
 int n,m,k=atoi(argv[2]);double cap=atof(argv[3]);mt19937 rng(atoi(argv[4]));string prefix=argv[5];
 ifstream in(argv[1]);in>>n>>m;vector<vector<int>> A(m,vector<int>(n)),inc(n*n);
 for(int i=0;i<m;i++)for(int r=0;r<n;r++){in>>A[i][r];inc[r*n+A[i][r]].push_back(i);}
 vector<int> score(m),cnt(n*n),tabu(m),sol(k),bestsol;vector<char> selected(m);
 auto update=[&](int v,int d){for(int r=0;r<n;r++){int cell=r*n+A[v][r];cnt[cell]+=d;for(int w:inc[cell])score[w]+=d;}};
 int energy=0,best=100000,steps=0,restarts=0;uint64_t iterations=0;
 auto start=chrono::steady_clock::now();auto seconds=[&](){return chrono::duration<double>(chrono::steady_clock::now()-start).count();};
 auto save=[&](bool witness){
  ofstream f(prefix+(witness?".witness.json":".best.json"));
  f<<"{\"order\":"<<n<<",\"size\":"<<k<<",\"index_base\":0,\"collision_pairs\":"<<best<<",\"seconds\":"<<seconds()<<",\"iterations\":"<<iterations<<",\"catalogue_row_indices\":[";
  for(int i=0;i<k;i++)f<<(i?",":"")<<bestsol[i];f<<"],\"arrays\":[";
  for(int i=0;i<k;i++){f<<(i?",[":"[");for(int r=0;r<n;r++)f<<(r?",":"")<<A[bestsol[i]][r];f<<"]";}f<<"]}\n";
 };
 while(seconds()<cap){
  fill(score.begin(),score.end(),0);fill(cnt.begin(),cnt.end(),0);fill(selected.begin(),selected.end(),0);fill(tabu.begin(),tabu.end(),0);energy=0;steps=0;int stale=0;restarts++;
  for(int j=0;j<k;j++){int v;do{v=rng()%m;}while(selected[v]);energy+=score[v];sol[j]=v;selected[v]=1;update(v,1);}
  while(stale<20000 && seconds()<cap){
   iterations++;steps++;stale++;
   if(energy<best){best=energy;bestsol=sol;stale=0;save(best==0);cerr<<"best="<<best<<" iterations="<<iterations<<" restarts="<<restarts<<" seconds="<<seconds()<<"\n";if(!best)return 0;}
   vector<int> victims;for(int j=0;j<k;j++)if(score[sol[j]]>n)victims.push_back(j);
   if(victims.empty()){cerr<<"energy mismatch\n";return 3;}
   int slot=victims[rng()%victims.size()],old=sol[slot];energy-=score[old]-n;selected[old]=0;update(old,-1);tabu[old]=steps+7+rng()%17;
   int value=100000,choice=-1,ties=0;
   for(int v=0;v<m;v++)if(!selected[v] && (tabu[v]<=steps || energy+score[v]<best)){
    if(score[v]<value){value=score[v];choice=v;ties=1;}
    else if(score[v]==value && rng()%++ties==0)choice=v;
   }
   if(choice<0){do{choice=rng()%m;}while(selected[choice]);}
   if(rng()%1000==0){do{choice=rng()%m;}while(selected[choice]);}
   energy+=score[choice];sol[slot]=choice;selected[choice]=1;update(choice,1);
  }
 }
 save(false);cerr<<"TIMEOUT best="<<best<<" iterations="<<iterations<<" seconds="<<seconds()<<"\n";
}
