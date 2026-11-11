// A local induced graph held in compile-time fixed words. No pruning changes.
#ifndef LOCAL_THRESHOLD
#define LOCAL_THRESHOLD 128
#endif
constexpr int LOCAL_WORDS=(LOCAL_THRESHOLD+63)/64;
struct LocalMask {
 uint64_t w[LOCAL_WORDS];
 bool any()const{for(auto x:w)if(x)return true;return false;}
 int first()const{for(int k=0;k<LOCAL_WORDS;k++)if(w[k])return 64*k+__builtin_ctzll(w[k]);return -1;}
 int count()const{int z=0;for(auto x:w)z+=__builtin_popcountll(x);return z;}
 void set(int v){w[v>>6]|=uint64_t(1)<<(v&63);}
 void erase(int v){w[v>>6]&=~(uint64_t(1)<<(v&63));}
 void subtract(const LocalMask& b){for(int k=0;k<LOCAL_WORDS;k++)w[k]&=~b.w[k];}
 LocalMask both(const LocalMask& b)const{LocalMask r;for(int k=0;k<LOCAL_WORDS;k++)r.w[k]=w[k]&b.w[k];return r;}
 int count_both(const LocalMask& b)const{int z=0;for(int k=0;k<LOCAL_WORDS;k++)z+=__builtin_popcountll(w[k]&b.w[k]);return z;}
};
struct Local64 {
 int size,ids[LOCAL_THRESHOLD];LocalMask edge[LOCAL_THRESHOLD],cells[31][31],initial{};
 Local64(const Bits& p){
  size=0;for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int v=64*j+__builtin_ctzll(w);w&=w-1;ids[size]=v;initial.set(size++);}}
  for(int r=0;r<n;r++)for(int c=0;c<n;c++)cells[r][c]=LocalMask{};
  for(int v=0;v<size;v++)for(int r=0;r<n;r++)cells[r][a[ids[v]][r]].set(v);
  for(int v=0;v<size;v++){
   LocalMask conflicts{};
   for(int r=0;r<n;r++)for(int k=0;k<LOCAL_WORDS;k++)conflicts.w[k]|=cells[r][a[ids[v]][r]].w[k];
   for(int k=0;k<LOCAL_WORDS;k++)edge[v].w[k]=initial.w[k]&~conflicts.w[k];
  }

 }
 int greedy(LocalMask p,int* order,int* bounds){
  int count=0,colour=0;
  while(p.any()){colour++;LocalMask available=p;while(available.any()){int v=available.first();order[count]=v;bounds[count++]=colour;p.erase(v);available.erase(v);available.subtract(edge[v]);}}
  return count;
 }
 int row(LocalMask p,int r,int* order,int* bounds){
  int used[31],counts[31],nc=0,len=0;LocalMask groups[31];
  for(int c=0;c<n;c++){groups[c]=p.both(r<n?cells[r][c]:cells[c][r-n]);if(groups[c].any()){counts[c]=groups[c].count();used[nc++]=c;}}
  sort(used,used+nc,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:groups[x].first()<groups[y].first();});
  for(int c=0;c<nc;c++){LocalMask g=groups[used[c]];while(g.any()){int v=g.first();g.erase(v);order[len]=v;bounds[len++]=c+1;}}
  return len;
 }
 int colour(LocalMask p,int need,int* order,int* bounds){
  int go[LOCAL_THRESHOLD],gb[LOCAL_THRESHOLD],gl=greedy(p,go,gb);
  if(gl && gb[gl-1]<need){emit(254);return 0;}
  int bestscore=1000000000,bestrow=0;
  for(int r=0;r<2*n;r++){
   int counts[31],nc=0;
   for(int c=0;c<n;c++){int count=p.count_both(r<n?cells[r][c]:cells[c][r-n]);if(count)counts[nc++]=count;}
   if(nc<need){emit((unsigned char)r);return 0;}
   int score=0;
   if(nc-need+1<=2){int lo=1000000000,second=1000000000;for(int c=0;c<nc;c++){int z=counts[c];if(z<lo){second=lo;lo=z;}else if(z<second)second=z;}score=lo;if(nc>=need+1)score+=second;}
   else {sort(counts,counts+nc,greater<int>());for(int c=need-1;c<nc;c++)score+=counts[c];}
   if(score<bestscore){bestscore=score;bestrow=r;}
  }
  int gs=0;for(int i=0;i<gl;i++)gs+=(gb[i]>=need);
  if(gs<bestscore){emit(254);copy(go,go+gl,order);copy(gb,gb+gl,bounds);return gl;}
  emit((unsigned char)bestrow);return row(p,bestrow,order,bounds);
 }
 bool expand(LocalMask p){
  if(!enter_node())return false;int need=target-(int)path.size();
  if(need==0){answer=path;return true;}
  if(p.count()<need){emit(253);return false;}
  int order[LOCAL_THRESHOLD],bounds[LOCAL_THRESHOLD],len=colour(p,need,order,bounds);
  for(int k=len-1;k>=0;k--){if(bounds[k]<need)return false;int v=order[k];path.push_back(ids[v]);if(need==1){answer=path;return true;}
   if(expand(p.both(edge[v])))return true;path.pop_back();if(timeout||root_cut)return false;p.erase(v);
  }return false;
 }
};
