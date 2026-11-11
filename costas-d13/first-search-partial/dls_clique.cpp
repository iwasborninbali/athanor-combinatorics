// Dynamic-penalty clique local search. Witness discovery only.
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
 if(argc<6){cerr<<"usage: dls_clique catalogue target seconds seed prefix\n";return 2;}
 int n,m,target=atoi(argv[2]),seed=atoi(argv[4]);double cap=atof(argv[3]);string prefix=argv[5];mt19937 rng(seed);
 ifstream in(argv[1]);in>>n>>m;vector<vector<int>> a(m,vector<int>(n));for(auto&x:a)for(int&y:x)in>>y;if(!in)return 2;
 int W=(m+63)/64;vector<vector<uint64_t>> adj(m,vector<uint64_t>(W));
 for(int i=0;i<m;i++)for(int j=0;j<i;j++){
  bool ok=true;for(int r=0;r<n;r++)if(a[i][r]==a[j][r]){ok=false;break;}
  if(ok){adj[i][j>>6]|=1ULL<<(j&63);adj[j][i>>6]|=1ULL<<(i&63);}
 }
 vector<int> bad(m),penalty(m),tabu(m),clique,best;vector<char> inside(m);
 uint64_t iterations=0,perturbations=0;int iteration=0;
 auto started=chrono::steady_clock::now();auto elapsed=[&](){return chrono::duration<double>(chrono::steady_clock::now()-started).count();};
 auto adjacent=[&](int u,int v){return (adj[u][v>>6]>>(v&63))&1;};
 auto add=[&](int v){inside[v]=1;clique.push_back(v);for(int w=0;w<m;w++)if(!adjacent(v,w))bad[w]++;};
 auto remove=[&](int v){inside[v]=0;clique.erase(find(clique.begin(),clique.end(),v));for(int w=0;w<m;w++)if(!adjacent(v,w))bad[w]--;tabu[v]=iteration+5+rng()%10;};
 auto choose=[&](int conflicts){
  int choice=-1,value=100000000,ties=0;
  for(int v=0;v<m;v++)if(!inside[v] && bad[v]==conflicts && (tabu[v]<=iteration || (conflicts==0&&clique.size()+1>best.size()))){
   if(penalty[v]<value){value=penalty[v];choice=v;ties=1;}
   else if(penalty[v]==value && rng()%++ties==0)choice=v;
  }return choice;
 };
 auto save=[&](){
  ofstream out(prefix+"_"+to_string(best.size())+".witness.json");
  out<<"{\"order\":"<<n<<",\"size\":"<<best.size()<<",\"index_base\":0,\"catalogue_row_indices\":[";
  for(int j=0;j<(int)best.size();j++)out<<(j?",":"")<<best[j];out<<"],\"arrays\":[";
  for(int j=0;j<(int)best.size();j++){out<<(j?",[":"[");for(int r=0;r<n;r++)out<<(r?",":"")<<a[best[j]][r];out<<"]";}out<<"]}\n";
 };
 add(rng()%m);int stale=0;
 while(elapsed()<cap){
  iterations++;iteration++;stale++;
  int v=choose(0);
  if(v>=0){add(v);stale=0;
   if(clique.size()>best.size()){best=clique;save();cerr<<"best="<<best.size()<<" iterations="<<iterations<<" seconds="<<elapsed()<<"\n";if((int)best.size()>=target)break;}
   continue;
  }
  v=choose(1);
  if(v>=0 && stale<100){
   int victim=-1;for(int u:clique)if(!adjacent(u,v)){victim=u;break;}
   if(victim<0){cerr<<"counter mismatch\n";return 3;}
   remove(victim);add(v);continue;
  }
  perturbations++;stale=0;
  for(int u:clique)penalty[u]++;
  if(perturbations%4==0)for(int&p:penalty)if(p)p--;
  // Keep a random current vertex, or occasionally two compatible ones.
  int retain=clique.empty()?-1:clique[rng()%clique.size()];
  vector<int> old=clique;for(int u:old)if(u!=retain)remove(u);
  if(retain<0)add(rng()%m);
  if(perturbations%32==0){old=clique;for(int u:old)remove(u);add(rng()%m);}
 }
 ofstream result(prefix+".json");result<<"{\"order\":"<<n<<",\"target\":"<<target<<",\"best\":"<<best.size()<<",\"seed\":"<<seed<<",\"iterations\":"<<iterations<<",\"perturbations\":"<<perturbations<<",\"seconds\":"<<elapsed()<<",\"status\":\""<<((int)best.size()>=target?"WITNESS":"TIMEOUT")<<"\"}\n";
 cerr<<"finished best="<<best.size()<<" seconds="<<elapsed()<<"\n";
}
