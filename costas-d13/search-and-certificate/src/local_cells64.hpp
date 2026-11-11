// Fixed local universe, exact catalogue order. Canonical trace-compatible.
#ifndef LOCAL_THRESHOLD
#define LOCAL_THRESHOLD 64
#endif
static_assert(LOCAL_THRESHOLD<=64);
struct Local64 {
 int size,ids[64];uint64_t edge[64],cells[31][31],initial;
 Local64(const Bits& p){
  size=0;for(int j=0;j<W;j++){uint64_t w=p[j];while(w){int v=64*j+__builtin_ctzll(w);w&=w-1;ids[size++]=v;}}
  initial=size==64?~uint64_t(0):(uint64_t(1)<<size)-1;
  for(int r=0;r<n;r++)for(int c=0;c<n;c++)cells[r][c]=0;
  for(int v=0;v<size;v++)for(int r=0;r<n;r++)cells[r][a[ids[v]][r]]|=uint64_t(1)<<v;
  for(int v=0;v<size;v++){uint64_t conflicts=0;for(int r=0;r<n;r++)conflicts|=cells[r][a[ids[v]][r]];edge[v]=initial&~conflicts;}

 }
 int greedy(uint64_t p,int* order,int* bounds){
  int count=0,colour=0;
  while(p){colour++;uint64_t available=p;while(available){int v=__builtin_ctzll(available);uint64_t bit=uint64_t(1)<<v;order[count]=v;bounds[count++]=colour;p^=bit;available&=~(edge[v]|bit);}}
  return count;
 }
 int row(uint64_t p,int r,int* order,int* bounds){
  int used[31],counts[31],nc=0,len=0;uint64_t groups[31];
  for(int c=0;c<n;c++)if((groups[c]=p&(r<n?cells[r][c]:cells[c][r-n]))){counts[c]=__builtin_popcountll(groups[c]);used[nc++]=c;}
  sort(used,used+nc,[&](int x,int y){return counts[x]!=counts[y]?counts[x]>counts[y]:__builtin_ctzll(groups[x])<__builtin_ctzll(groups[y]);});
  for(int c=0;c<nc;c++){uint64_t g=groups[used[c]];while(g){int v=__builtin_ctzll(g);g&=g-1;order[len]=v;bounds[len++]=c+1;}}
  return len;
 }
 int colour(uint64_t p,int need,int* order,int* bounds){
  int go[64],gb[64],gl=greedy(p,go,gb);
  if(gl && gb[gl-1]<need){emit(254);return 0;}
  int bestscore=1000000000,bestrow=0;
  for(int r=0;r<2*n;r++){
   int counts[31],nc=0;
   for(int c=0;c<n;c++){int count=__builtin_popcountll(p&(r<n?cells[r][c]:cells[c][r-n]));if(count)counts[nc++]=count;}
   if(nc<need){emit((unsigned char)r);return 0;}
   // Only nc-need+1 smallest groups contribute to the branch suffix.
   sort(counts,counts+nc,greater<int>());int score=0;for(int c=need-1;c<nc;c++)score+=counts[c];
   if(score<bestscore){bestscore=score;bestrow=r;}
  }
  int gs=0;for(int i=0;i<gl;i++)gs+=(gb[i]>=need);
  if(gs<bestscore){emit(254);copy(go,go+gl,order);copy(gb,gb+gl,bounds);return gl;}
  emit((unsigned char)bestrow);return row(p,bestrow,order,bounds);
 }
 bool expand(uint64_t p){
  if(!enter_node())return false;int need=target-(int)path.size();
  if(need==0){answer=path;return true;}
  if(__builtin_popcountll(p)<need){emit(253);return false;}
  int order[64],bounds[64],len=colour(p,need,order,bounds);
  for(int k=len-1;k>=0;k--){if(bounds[k]<need)return false;int v=order[k];path.push_back(ids[v]);if(need==1){answer=path;return true;}
   if(expand(p&edge[v]))return true;path.pop_back();if(timeout||root_cut)return false;p&=~(uint64_t(1)<<v);
  }return false;
 }
};
