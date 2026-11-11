// Cyclic row/column translation construction families. Discovery only.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
bool costas(const vector<int>& p){
 int n=p.size();for(int d=1;d<n;d++){
  uint64_t seen=0;for(int r=0;r+d<n;r++){
   uint64_t bit=1ULL<<(p[r+d]-p[r]+n);if(seen&bit)return false;seen|=bit;
  }
 }return true;
}
int main(int argc,char**argv){
 if(argc<3)return 2;ifstream in(argv[1]);int n,m;in>>n>>m;vector<vector<int>> a(m,vector<int>(n));for(auto&p:a)for(int&v:p)in>>v;
 int best=0,good_lines=0;string prefix=argv[2];
 for(int index=0;index<m;index++)for(int direction=-1;direction<n;direction++){
  // direction=-1 is pure column translation; otherwise (row shift t,
  // column shift direction*t), modulo n. Require the entire line disjoint.
  uint64_t distinct=0;
  for(int r=0;r<n;r++)distinct|=1ULL<<((a[index][r]+(direction<0?0:direction*r))%n);
  if(direction>=0 && __builtin_popcountll(distinct)!=n)continue;
  good_lines++;vector<vector<int>> family;
  for(int t=0;t<n;t++){
   vector<int> p(n);for(int r=0;r<n;r++)p[r]=(a[index][(r+(direction<0?0:t))%n]+(direction<0?t:direction*t))%n;
   if(costas(p))family.push_back(p);
  }
  if((int)family.size()<=best)continue;
  best=family.size();ofstream out(prefix+".witness.json");out<<"{\"order\":"<<n<<",\"size\":"<<best<<",\"index_base\":0,\"arrays\":[";
  for(int j=0;j<best;j++){out<<(j?",[":"[");for(int r=0;r<n;r++)out<<(r?",":"")<<family[j][r];out<<"]";}out<<"]}\n";
  cerr<<"best="<<best<<" base="<<index<<" direction="<<direction<<"\n";
 }
 ofstream result(prefix+".json");result<<"{\"order\":"<<n<<",\"best\":"<<best<<",\"disjoint_translation_lines_examined\":"<<good_lines<<",\"scope\":\"cyclic translation lines through catalogue arrays only\"}\n";
 cout<<best<<"\n";
}
