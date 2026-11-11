// Exhaustively generate Costas permutations, without symmetry reductions.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <chrono>
using namespace std;
int n;
uint64_t nodes=0, leaves=0;
int permutation[30];
uint64_t differences[30]{};
ofstream result;
void generate(int length, uint32_t used) {
  ++nodes;
  if(length==n) {
    ++leaves;
    for(int r=0;r<n;++r) result<<(r?" ":"")<<permutation[r];
    result<<'\n'; return;
  }
  for(int c=0;c<n;++c) if(!(used & (uint32_t(1)<<c))) {
    bool valid=true;
    for(int d=1;d<=length;++d) if(differences[d] & (uint64_t(1)<<(c-permutation[length-d]+n))) {valid=false;break;}
    if(!valid) continue;
    for(int d=1;d<=length;++d) differences[d] |= uint64_t(1)<<(c-permutation[length-d]+n);
    permutation[length]=c;
    generate(length+1,used|(uint32_t(1)<<c));
    for(int d=1;d<=length;++d) differences[d] ^= uint64_t(1)<<(c-permutation[length-d]+n);
  }
}
int main(int argc,char**argv) {
  if(argc!=3) return 2;
  n=stoi(argv[1]); if(n<2||n>29) return 2;
  result.open(argv[2]); if(!result) return 2;
  auto t=chrono::steady_clock::now();
  generate(0,0);
  result.close();
  cout<<"{\"order\":"<<n<<",\"arrays\":"<<leaves<<",\"prefixes\":"<<nodes<<",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-t).count()<<",\"symmetry\":false}\n";
}
