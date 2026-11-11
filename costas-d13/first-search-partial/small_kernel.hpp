// Representation-only acceleration. Local vertices preserve global index order.
struct PairBits {
 uint64_t lo=0,hi=0;
 bool any()const{return lo||hi;}
 int count()const{return __builtin_popcountll(lo)+__builtin_popcountll(hi);}
 int first()const{return lo?__builtin_ctzll(lo):64+__builtin_ctzll(hi);}
 void erase(int v){if(v<64)lo&=~(1ULL<<v);else hi&=~(1ULL<<(v-64));}
 void insert(int v){if(v<64)lo|=1ULL<<v;else hi|=1ULL<<(v-64);}
 PairBits both(PairBits b)const{return {lo&b.lo,hi&b.hi};}
 void subtract(PairBits b){lo&=~b.lo;hi&=~b.hi;}
};
struct SmallKernel {
 int size,ids[128],keys[128][62];PairBits edges[128],initial;
 SmallKernel(const Bits& p){
  size=0;for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int v=64*j+__builtin_ctzll(w);w&=w-1;ids[size]=v;for(int r=0;r<2*n;r++)keys[size][r]=partition_keys[v][r];initial.insert(size++);}}
  for(int v=0;v<size;v++)for(int u=0;u<size;u++)if(adj[ids[v]][ids[u]>>6]>>(ids[u]&63)&1)edges[v].insert(u);
 }
 int greedy(PairBits p,int* order,int* bounds){
  int len=0,col=0;while(p.any()){++col;PairBits avail=p;while(avail.any()){int v=avail.first();order[len]=v;bounds[len++]=col;p.erase(v);avail.erase(v);avail.subtract(edges[v]);}}
  return len;
 }
 int row(PairBits p,int r,int* order,int* bounds){
  PairBits group[31];int used[31],len=0,nu=0;
  while(p.any()){int v=p.first();p.erase(v);group[keys[v][r]].insert(v);}
  for(int c=0;c<n;c++)if(group[c].any())used[nu++]=c;
  sort(used,used+nu,[&](int x,int y){int cx=group[x].count(),cy=group[y].count();return cx!=cy?cx>cy:group[x].first()<group[y].first();});
  for(int i=0;i<nu;i++){PairBits g=group[used[i]];while(g.any()){int v=g.first();g.erase(v);order[len]=v;bounds[len++]=i+1;}}
  return len;
 }
 bool decode(PairBits p,int need,int* order,int* bounds,int& len,bool& closed){
  if(!replaying)return false;int op=gzgetc(replay_input);
  if(op<0){int code;gzerror(replay_input,&code);if(code!=Z_OK&&code!=Z_STREAM_END){cerr<<"bad local replay gzip\n";exit(5);}gzclose(replay_input);replay_input=nullptr;replaying=false;proof=gzopen((output_prefix+".proof.gz").c_str(),"ab1");if(!proof)exit(5);cerr<<"replay_finished nodes="<<replayed_nodes<<" seconds="<<elapsed()<<"\n";return false;}
  replayed_nodes++;
  if(op==253){if(p.count()>=need){cerr<<"invalid local cardinality\n";exit(5);}closed=true;return true;}
  if(op==254)len=greedy(p,order,bounds);
  else if(op<2*n)len=row(p,op,order,bounds);
  else {cerr<<"unsupported local replay opcode "<<op<<"\n";exit(5);}
  return true;
 }
 int colour(PairBits p,int need,int* order,int* bounds){
  int bestscore=1000000000,bestrow=0;
  for(int r=0;r<2*n;r++){
   int sizes[31]={},positive[31],count=0;PairBits q=p;
   while(q.any()){int v=q.first();q.erase(v);sizes[keys[v][r]]++;}
   for(int c=0;c<n;c++)if(sizes[c])positive[count++]=sizes[c];
   if(count<need){bestscore=-1;bestrow=r;break;}
   sort(positive,positive+count,greater<int>());int score=0;for(int c=max(0,need-1);c<count;c++)score+=positive[c];
   if(score<bestscore){bestscore=score;bestrow=r;}
  }
  int go[128],gb[128],gl=0,gs=0;if(bestscore>=0)gl=greedy(p,go,gb);
  for(int i=0;i<gl;i++)if(gb[i]>=need)gs++;
  if(gs<bestscore){emit(254);copy(go,go+gl,order);copy(gb,gb+gl,bounds);return gl;}
  emit((unsigned char)bestrow);return row(p,bestrow,order,bounds);
 }
 bool expand(PairBits p){
  if(!enter_node())return false;int need=target-(int)path.size();if(!need){answer=path;return true;}
  if(best_lower<target-1 && (int)path.size()>=target-3){vector<int> trial=path;PairBits q=p;while(q.any()&&(int)trial.size()<target){int v=q.first();trial.push_back(ids[v]);q=q.both(edges[v]);}if((int)trial.size()>best_lower){best_lower=trial.size();save_witness(trial,output_prefix+".lower.witness.json");cerr<<"lower_witness="<<best_lower<<" nodes="<<nodes<<" seconds="<<elapsed()<<"\n";}if((int)trial.size()>=target){answer=trial;return true;}}
  int order[128],bounds[128],len=0;bool closed=false,decoded=decode(p,need,order,bounds,len,closed);if(closed)return false;
  if(!decoded){if(p.count()<need){emit(253);return false;}len=colour(p,need,order,bounds);}
  for(int k=len-1;k>=0;k--){if(bounds[k]<need)return false;int v=order[k];path.push_back(ids[v]);if(need==1){answer=path;return true;}if(expand(p.both(edges[v])))return true;path.pop_back();if(timeout||root_cut)return false;p.erase(v);}
  return false;
 }
};
