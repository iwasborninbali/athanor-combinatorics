from pathlib import Path
p=Path('check_trace.cpp')
s=p.read_text()
Path('logs/check_trace_before_stack.cpp').write_text(s)
pos=s.index(' void node(const vector<int>& vertices,int need){')
small=r'''
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
'''
s=s[:pos]+small+s[pos:]
s=s.replace(' void node(const vector<int>& vertices,int need){\n',' void node(const vector<int>& vertices,int need){\n  if(vertices.size()<=128){small_node(vertices.data(),vertices.size(),need);return;}\n',1)
p.write_text(s)
