// Search acceleration using sorted small candidate vectors, with identical
// partition choices and canonical branch order to the general bitset engine.
bool expand_small_vector(const int* vertices,int length){
 if(!enter_node())return false;int need=target-(int)path.size();if(!need){answer=path;return true;}
 if(best_lower<target-1 && (int)path.size()>=target-3){
  vector<int> trial=path;int pending[128],next[128],len=length;copy(vertices,vertices+length,pending);
  while(len&&(int)trial.size()<target){int v=pending[0];trial.push_back(v);int count=0;for(int j=1;j<len;j++)if(adj[v][pending[j]>>6]>>(pending[j]&63)&1)next[count++]=pending[j];copy(next,next+count,pending);len=count;}
  if((int)trial.size()>best_lower){best_lower=trial.size();save_witness(trial,output_prefix+".lower.witness.json");}
  if((int)trial.size()>=target){answer=trial;return true;}
 }
 int op=-1;
 if(replaying){
  op=gzgetc(replay_input);if(op<0){int code;gzerror(replay_input,&code);if(code!=Z_OK&&code!=Z_STREAM_END){cerr<<"bad vector replay gzip\n";exit(5);}gzclose(replay_input);replay_input=nullptr;replaying=false;proof=gzopen((output_prefix+".proof.gz").c_str(),"ab1");if(!proof)exit(5);cerr<<"replay_finished nodes="<<replayed_nodes<<" seconds="<<elapsed()<<"\n";}
  else replayed_nodes++;
 }
 if(op==253){if(length>=need){cerr<<"invalid cardinality replay\n";exit(5);}return false;}
 if(op<0&&length<need){emit(253);return false;}
 int go[128],gb[128],gl=0,gs=0;
 auto greedy=[&](){bool used[128]={};int done=0,col=0;while(done<length){++col;int members[128],count=0;for(int i=0;i<length;i++)if(!used[i]){bool ok=true;for(int j=0;j<count;j++)if(adj[vertices[i]][vertices[members[j]]>>6]>>(vertices[members[j]]&63)&1){ok=false;break;}if(ok){members[count++]=i;go[gl]=i;gb[gl++]=col;used[i]=true;done++;}}}};
 if(op<0){
  greedy();
  if(gl && gb[gl-1]<need){emit(254);return false;}
  int bestscore=1000000000,bestrow=0;
  for(int r=0;r<2*n;r++){
   int sizes[31]={},positive[31],count=0;for(int i=0;i<length;i++)sizes[partition_keys[vertices[i]][r]]++;
   for(int c=0;c<n;c++)if(sizes[c])positive[count++]=sizes[c];if(count<need){bestscore=-1;bestrow=r;break;}
   sort(positive,positive+count,greater<int>());int score=0;for(int c=max(0,need-1);c<count;c++)score+=positive[c];if(score<bestscore){bestscore=score;bestrow=r;}
  }
  if(bestscore>=0 && !gl)greedy();for(int i=0;i<gl;i++)if(gb[i]>=need)gs++;
  op=gs<bestscore?254:bestrow;emit((unsigned char)op);
 }
 int order[128],bounds[128],len=0;
 if(op==254){if(!gl)greedy();len=gl;copy(go,go+gl,order);copy(gb,gb+gl,bounds);}
 else if(op<2*n){
  int counts[31]={},groups[31][128],ids[31],nc=0;
  for(int i=0;i<length;i++){int c=partition_keys[vertices[i]][op];groups[c][counts[c]++]=i;}
  for(int c=0;c<n;c++)if(counts[c])ids[nc++]=c;
  sort(ids,ids+nc,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:groups[x][0]<groups[y][0];});
  for(int c=0;c<nc;c++)for(int j=0;j<counts[ids[c]];j++){order[len]=groups[ids[c]][j];bounds[len++]=c+1;}
 }else{cerr<<"unsupported small vector opcode "<<op<<"\n";exit(5);}
 bool active[128];fill(active,active+length,true);int child[128];
 for(int k=len-1;k>=0;k--){if(bounds[k]<need)return false;int i=order[k],v=vertices[i];path.push_back(v);if(need==1){answer=path;return true;}int count=0;for(int j=0;j<length;j++)if(active[j]&&(adj[v][vertices[j]>>6]>>(vertices[j]&63)&1))child[count++]=vertices[j];if(expand_small_vector(child,count))return true;path.pop_back();if(timeout||root_cut)return false;active[i]=false;}
 return false;
}
