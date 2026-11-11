// Direct binary-conflict encoding of the same exact-cover model.
// One process, streaming gzip output, no solver dependency.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
#include <zlib.h>
using namespace std;
int main(int argc,char**argv){
 if(argc<3){cerr<<"usage: make_pairwise_cnf catalogue output.cnf.gz [full]\n";return 2;}
 ifstream in(argv[1]);int n,m;in>>n>>m;bool full=argc>3&&string(argv[3])=="full";
 vector<vector<int>> a(m,vector<int>(n)),cells(n*n);
 for(int i=0;i<m;i++)for(int r=0;r<n;r++){in>>a[i][r];cells[r*n+a[i][r]].push_back(i+1);}
 if(!in)return 2;
 int W=(m+63)/64;vector<vector<uint64_t>> conflict(m,vector<uint64_t>(W));uint64_t pairs=0;
 for(int i=0;i<m;i++)for(int j=0;j<i;j++){
  bool hit=false;for(int r=0;r<n;r++)if(a[i][r]==a[j][r]){hit=true;break;}
  if(hit){conflict[i][j>>6]|=1ULL<<(j&63);pairs++;}
 }
 map<vector<int>,int> lookup;for(int i=0;i<m;i++)lookup[a[i]]=i;
 vector<int> representative(m);int noncanonical=0;
 for(int i=0;i<m;i++){
  int best=i;auto b=a[i];for(int turn=0;turn<4;turn++){
   best=min(best,lookup.at(b));auto reflected=b;for(int&x:reflected)x=n-1-x;best=min(best,lookup.at(reflected));
   vector<int> rot(n);for(int r=0;r<n;r++)rot[b[r]]=n-1-r;b=rot;
  }representative[i]=best;noncanonical+=(best<i);
 }
 uint64_t clauses=pairs+(uint64_t)n*m+n*n+(full?n*n:2*n+(uint64_t)n*n*(n-1))+(3ULL*m-1)+noncanonical;
 int variables=2*m+n*n,prefix_start=m+n*n+1;
 gzFile out=gzopen(argv[2],"wb1");if(!out)return 3;gzbuffer(out,1<<20);
 gzprintf(out,"p cnf %d %llu\n",variables,(unsigned long long)clauses);
 uint64_t emitted=0;
 auto binary=[&](int x,int y){gzprintf(out,"%d %d 0\n",x,y);emitted++;};
 auto unit=[&](int x){gzprintf(out,"%d 0\n",x);emitted++;};
 for(int i=0;i<m;i++)for(int w=0;w<W;w++){
  uint64_t mask=conflict[i][w];while(mask){int b=__builtin_ctzll(mask),j=64*w+b;binary(-i-1,-j-1);mask&=mask-1;}
 }
 for(int i=0;i<m;i++)for(int r=0;r<n;r++)binary(-i-1,-m-1-r*n-a[i][r]);
 for(int cell=0;cell<n*n;cell++){
  for(int v:cells[cell])gzprintf(out,"%d ",v);gzprintf(out,"%d 0\n",m+cell+1);emitted++;
 }
 if(full){for(int c=0;c<n*n;c++)unit(-m-1-c);}
 else{
  for(int r=0;r<n;r++){for(int c=0;c<n;c++)gzprintf(out,"%d ",m+1+r*n+c);gzprintf(out,"0\n");emitted++;}
  for(int c=0;c<n;c++){for(int r=0;r<n;r++)gzprintf(out,"%d ",m+1+r*n+c);gzprintf(out,"0\n");emitted++;}
  for(int r=0;r<n;r++)for(int c=0;c<n;c++)for(int d=0;d<c;d++)binary(-m-1-r*n-c,-m-1-r*n-d);
  for(int c=0;c<n;c++)for(int r=0;r<n;r++)for(int s=0;s<r;s++)binary(-m-1-r*n-c,-m-1-s*n-c);
 }
 binary(-prefix_start,1);binary(-1,prefix_start);
 for(int i=1;i<m;i++){
  binary(-prefix_start-i+1,prefix_start+i);binary(-i-1,prefix_start+i);
  gzprintf(out,"%d %d %d 0\n",-prefix_start-i,prefix_start+i-1,i+1);emitted++;
 }
 for(int i=0;i<m;i++)if(representative[i]<i)binary(-i-1,prefix_start+representative[i]);
 int code=gzclose(out);if(code!=Z_OK||emitted!=clauses){cerr<<"bad write or count "<<emitted<<" "<<clauses<<"\n";return 3;}
 cout<<"{\"order\":"<<n<<",\"arrays\":"<<m<<",\"variables\":"<<variables<<",\"clauses\":"<<clauses<<",\"conflict_pairs\":"<<pairs<<",\"full\":"<<(full?"true":"false")<<"}\n";
}
