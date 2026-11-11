// Independent trace verifier. No search code is included or linked.
// Candidate sets are sorted vectors, graph construction is by cell incidence,
// and canonical greedy classes are decoded by a first-fit vector scan.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#include <zlib.h>
using namespace std;
void require(bool ok,const char* message){if(!ok)throw runtime_error(message);}
struct Trace {
 gzFile f;unsigned char buffer[65536];int pos=0,length=0;
 explicit Trace(const char* path):f(gzopen(path,"rb")){require(f,"cannot open trace");}
 int next(){
  if(pos==length){length=gzread(f,buffer,sizeof(buffer));pos=0;require(length>=0,"gzip read failure");if(!length){int error;gzerror(f,&error);require(error==Z_OK||error==Z_STREAM_END,"truncated or corrupt gzip");return -1;}}
  return buffer[pos++];
 }
 int byte(){int c=next();require(c>=0,"truncated trace");return c;}
 ~Trace(){if(f)gzclose(f);}
};
struct Audit {
 int n,m,target,words;vector<vector<int>> arrays,inverse;
 vector<vector<uint64_t>> neighbors;vector<int> representative,selection;
 uint64_t nodes=0,roots=0;chrono::steady_clock::time_point start;
 Trace& trace;
 Audit(const char* catalogue,int k,Trace& input):target(k),trace(input){
  ifstream f(catalogue);require(bool(f>>n>>m),"missing catalogue header");require(n>0&&n<32&&m>0&&target>1,"invalid parameters");
  arrays.assign(m,vector<int>(n));inverse=arrays;map<vector<int>,int> index;
  for(int v=0;v<m;v++){
   vector<bool> seen(n);for(int r=0;r<n;r++){int c;require(bool(f>>c)&&c>=0&&c<n&&!seen[c],"invalid permutation");seen[c]=true;arrays[v][r]=c;inverse[v][c]=r;}
   require(index.emplace(arrays[v],v).second,"duplicate catalogue array");
   vector<pair<int,int>> differences;for(int r=0;r<n;r++)for(int s=r+1;s<n;s++)differences.emplace_back(s-r,arrays[v][s]-arrays[v][r]);
   sort(differences.begin(),differences.end());require(adjacent_find(differences.begin(),differences.end())==differences.end(),"non-Costas catalogue row");
  }
  string extra;require(!(f>>extra),"extra catalogue entries");
  words=(m+63)/64;vector<vector<uint64_t>> incidence(n*n,vector<uint64_t>(words));
  for(int v=0;v<m;v++)for(int r=0;r<n;r++)incidence[r*n+arrays[v][r]][v/64]|=uint64_t(1)<<(v%64);
  neighbors.assign(m,vector<uint64_t>(words,~uint64_t(0)));
  for(int v=0;v<m;v++){
   if(m%64)neighbors[v].back()=(uint64_t(1)<<(m%64))-1;
   for(int r=0;r<n;r++)for(int b=0;b<words;b++)neighbors[v][b]&=~incidence[r*n+arrays[v][r]][b];
  }
  representative.resize(m);
  for(int v=0;v<m;v++){
   int smallest=v;vector<int> turn=arrays[v];
   for(int t=0;t<4;t++){
    auto found=index.find(turn);require(found!=index.end(),"catalogue not rotation-closed");smallest=min(smallest,found->second);
    vector<int> reflected(n);for(int r=0;r<n;r++)reflected[r]=n-1-turn[r];
    found=index.find(reflected);require(found!=index.end(),"catalogue not reflection-closed");smallest=min(smallest,found->second);
    vector<int> next(n);for(int r=0;r<n;r++)next[turn[r]]=n-1-r;turn=next;
   }representative[v]=smallest;
  }
  start=chrono::steady_clock::now();
 }
 bool edge(int u,int v)const{return (neighbors[u][v/64]>>(v%64))&1;}
 double seconds()const{return chrono::duration<double>(chrono::steady_clock::now()-start).count();}
 void hall(const vector<int>& vertices){
  require(target==n-1,"Hall opcode for wrong target");uint32_t mask=0;for(int b=0;b<4;b++)mask|=uint32_t(trace.byte())<<(8*b);
  uint32_t full=(uint32_t(1)<<n)-1;require(mask && !(mask&~full),"invalid Hall row mask");
  vector<uint32_t> occupied(n),support(n),allowed(n);
  for(int v:selection)for(int r=0;r<n;r++){uint32_t bit=uint32_t(1)<<arrays[v][r];require(!(occupied[r]&bit),"selection not disjoint");occupied[r]|=bit;}
  for(int v:vertices)for(int r=0;r<n;r++){uint32_t bit=uint32_t(1)<<arrays[v][r];require(!(occupied[r]&bit),"invalid common candidate");support[r]|=bit;}
  uint32_t columns=0;
  for(int r=0;r<n;r++){uint32_t vacant=full^occupied[r],forced=vacant&~support[r];require(__builtin_popcount(forced)<=1,"invalid forced-hole claim");allowed[r]=forced?forced:vacant;if(mask>>r&1)columns|=allowed[r];}
  require(__builtin_popcount(columns)<__builtin_popcount(mask),"Hall inequality not deficient");
 }

 // Small certificates are decoded with bounded stack arrays. This performs
 // the same independent vector scan and coverage check without heap traffic.
 void small_node(const int* vertices,int length,int need){
  require(need>0,"target clique reached in refutation");nodes++;
  if(nodes%1048576==0)cerr<<"verified_nodes="<<nodes<<" seconds="<<seconds()<<"\n";
  int op=trace.byte();
  if(op==253){require(length<need,"invalid cardinality leaf");return;}
  if(op==252){vector<int> v(vertices,vertices+length);hall(v);return;}
  int members[128][128],counts[128]={},nc=0,ids[128];
  if(op<2*n){
   nc=n;
   for(int i=0;i<length;i++){int v=vertices[i],c=op<n?arrays[v][op]:inverse[v][op-n];members[c][counts[c]++]=i;}
   int used=0;for(int c=0;c<nc;c++)if(counts[c])ids[used++]=c;
   sort(ids,ids+used,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:members[x][0]<members[y][0];});nc=used;
  }else{
   require(op==254||op==251,"unknown trace opcode");bool assigned[128]={};int done=0;
   while(done<length){
    int colour=nc++;
    for(int i=0;i<length;i++)if(!assigned[i]){
     bool independent=true;for(int q=0;q<counts[colour];q++)if(edge(vertices[i],vertices[members[colour][q]])){independent=false;break;}
     if(independent){members[colour][counts[colour]++]=i;assigned[i]=true;done++;}
    }
    require(counts[colour]>0,"empty greedy class");
   }
   if(op==251){
    require(length<=64,"oversized recolouring node");int membership[128];for(int c=0;c<nc;c++)for(int j=0;j<counts[c];j++)membership[members[c][j]]=c;
    int moves=trace.byte();for(int j=0;j<moves;j++){
     int i=trace.byte(),dest=trace.byte();require(i<length&&dest<nc,"invalid recolouring index");
     for(int q=0;q<counts[dest];q++)require(!edge(vertices[i],vertices[members[dest][q]]),"improper recolouring move");
     int old=membership[i],at=0;while(at<counts[old]&&members[old][at]!=i)at++;require(at<counts[old],"missing recolouring member");
     for(int q=at+1;q<counts[old];q++)members[old][q-1]=members[old][q];counts[old]--;members[dest][counts[dest]++]=i;membership[i]=dest;
    }
    for(int c=0;c<nc;c++)sort(members[c],members[c]+counts[c]);
   }
   int used=0;for(int c=0;c<nc;c++)if(counts[c])ids[used++]=c;nc=used;
  }
  bool active[128];fill(active,active+length,true);int covered=0;for(int c=0;c<nc;c++)covered+=counts[ids[c]];require(covered==length,"colour coverage failure");
  int child[128];
  for(int colour=nc;colour>=need;colour--){int c=ids[colour-1];for(int k=counts[c]-1;k>=0;k--){
   require(need>1,"certificate omits an existing target clique");int i=members[c][k],v=vertices[i];require(active[i],"repeated branch vertex");
   int len=0;for(int j=0;j<length;j++)if(active[j]&&edge(v,vertices[j]))child[len++]=vertices[j];
   selection.push_back(v);small_node(child,len,need-1);selection.pop_back();active[i]=false;
  }}
 }
 void node(const vector<int>& vertices,int need){
  if(vertices.size()<=128){small_node(vertices.data(),vertices.size(),need);return;}
  require(need>0,"target clique reached in refutation");nodes++;
  if(nodes%1048576==0)cerr<<"verified_nodes="<<nodes<<" seconds="<<seconds()<<"\n";
  int op=trace.byte();
  if(op==253){require((int)vertices.size()<need,"invalid cardinality leaf");return;}
  if(op==252){hall(vertices);return;}
  vector<vector<int>> classes;
  if(op<2*n){
   classes.resize(n);
   for(int i=0;i<(int)vertices.size();i++){int v=vertices[i],cell=op<n?arrays[v][op]:inverse[v][op-n];classes[cell].push_back(i);}
   classes.erase(remove_if(classes.begin(),classes.end(),[](const auto& group){return group.empty();}),classes.end());
   sort(classes.begin(),classes.end(),[](const auto& x,const auto& y){return x.size()!=y.size()?x.size()>y.size():x.front()<y.front();});
  }else{
   require(op==254||op==251,"unknown trace opcode");vector<int> remaining(vertices.size());for(int i=0;i<(int)remaining.size();i++)remaining[i]=i;
   while(!remaining.empty()){
    vector<int> colour,left;
    for(int i:remaining){bool independent=true;for(int j:colour)if(edge(vertices[i],vertices[j])){independent=false;break;}if(independent)colour.push_back(i);else left.push_back(i);}
    require(!colour.empty(),"empty greedy class");classes.push_back(std::move(colour));remaining=std::move(left);
   }
   if(op==251){
    require(vertices.size()<=64,"oversized recolouring node");vector<int> membership(vertices.size());for(int c=0;c<(int)classes.size();c++)for(int i:classes[c])membership[i]=c;
    int moves=trace.byte();for(int j=0;j<moves;j++){
     int i=trace.byte(),destination=trace.byte();require(i<(int)vertices.size()&&destination<(int)classes.size(),"invalid recolouring index");
     for(int other:classes[destination])require(!edge(vertices[i],vertices[other]),"improper recolouring move");
     int old=membership[i];auto at=find(classes[old].begin(),classes[old].end(),i);require(at!=classes[old].end(),"missing recolouring member");classes[old].erase(at);classes[destination].push_back(i);membership[i]=destination;
    }
    classes.erase(remove_if(classes.begin(),classes.end(),[](const auto& group){return group.empty();}),classes.end());for(auto& group:classes)sort(group.begin(),group.end());
   }
   // Independence is constructive: a new member is compared with every
   // earlier member above. Adjacency was independently reconstructed from
   // the validated cell incidences, rather than copied from the search.
  }
  vector<bool> active(vertices.size(),true);int covered=0;for(const auto& group:classes)covered+=group.size();require(covered==(int)vertices.size(),"colour coverage failure");
  for(int colour=(int)classes.size();colour>=need;colour--)for(auto it=classes[colour-1].rbegin();it!=classes[colour-1].rend();++it){
   require(need>1,"certificate omits an existing target clique");int i=*it,v=vertices[i];require(active[i],"repeated branch vertex");
   vector<int> child;child.reserve(vertices.size());for(int j=0;j<(int)vertices.size();j++)if(active[j]&&edge(v,vertices[j]))child.push_back(vertices[j]);
   selection.push_back(v);node(child,need-1);selection.pop_back();active[i]=false;
  }
 }
 void run(){
  for(int i=0;i<m;i++)if(representative[i]==i){
   vector<int> candidates;for(int j=i+1;j<m;j++)if(representative[j]>=i&&edge(i,j))candidates.push_back(j);
   selection={i};node(candidates,target-1);roots++;
  }
  for(char c:string("ENDPROOF"))require(trace.byte()==c,"missing completion marker");require(trace.next()<0,"trailing proof data");
  cout<<"{\"verified\":true,\"order\":"<<n<<",\"excluded_clique_size\":"<<target<<",\"nodes\":"<<nodes<<",\"roots\":"<<roots<<",\"seconds\":"<<seconds()<<"}\n";
 }
};
int main(int argc,char**argv){try{require(argc==4,"usage: check_trace catalogue trace.gz target");Trace trace(argv[2]);Audit audit(argv[1],stoi(argv[3]),trace);audit.run();return 0;}catch(const exception& e){cerr<<"REJECTED: "<<e.what()<<"\n";return 1;}}
