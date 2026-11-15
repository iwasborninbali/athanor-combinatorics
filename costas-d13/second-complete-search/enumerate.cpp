#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
struct Enumerator {
  int n; array<int, 16> p{}; array<uint32_t, 16> diff{};
  vector<array<uint8_t, 16>> arrays;
  uint64_t nodes = 0;
  explicit Enumerator(int n): n(n) {}
  void dfs(int row, uint32_t cols) {
    ++nodes;
    if (row == n) {
      array<uint8_t,16> x{};
      for(int i=0;i<n;i++) x[i] = p[i];
      arrays.push_back(x);
      return;
    }
    for(int col=0;col<n;col++) {
      if(cols & (1u << col)) continue;
      bool ok = true;
      for(int i=0;i<row;i++) {
        int d = row-i, delta=col-p[i];
        if(diff[d] & (1u << (delta+n-1))) { ok=false; break; }
      }
      if(!ok) continue;
      for(int i=0;i<row;i++) diff[row-i] |= (1u << (col-p[i]+n-1));
      p[row]=col;
      dfs(row+1,cols|(1u<<col));
      for(int i=0;i<row;i++) diff[row-i] ^= (1u << (col-p[i]+n-1));
    }
  }
};
int main(int argc,char **argv){
  string dest=argc>1?argv[1]:"catalogues";
  int maxn=argc>2?stoi(argv[2]):13;
  system(("mkdir -p "+dest).c_str());
  for(int n=1;n<=maxn;n++){
    auto before=chrono::steady_clock::now();
    Enumerator E(n); E.dfs(0,0);
    string fn=dest+"/costas"+to_string(n)+".bin";
    ofstream out(fn,ios::binary);
    for(const auto &a:E.arrays) out.write((const char*)a.data(), n);
    out.close();
    auto elapsed=chrono::duration<double>(chrono::steady_clock::now()-before).count();
    cout<<"n="<<n<<" count="<<E.arrays.size()<<" nodes="<<E.nodes<<" seconds="<<elapsed<<" file="<<fn<<endl;
  }
}
