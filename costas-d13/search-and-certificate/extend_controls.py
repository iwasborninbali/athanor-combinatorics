from pathlib import Path
for name in ['baseline/timed_baseline.cpp','src/clique_fast.cpp']:
 p=Path(name);s=p.read_text().replace('#include <map>','#include <map>\n#include <sstream>')
 s=s.replace('int main(int argc,char**argv){', '''int main(int argc,char**argv){
 vector<int> requested_roots;
 if(const char* raw=getenv("SPEED_ROOT_LIST")){string text=raw;replace(text.begin(),text.end(),',',' ');istringstream in(text);int q;while(in>>q)requested_roots.push_back(q);sort(requested_roots.begin(),requested_roots.end());}
''')
 s=s.replace('ordinal++;if(ordinal<root_begin', 'ordinal++;if(!requested_roots.empty() && !binary_search(requested_roots.begin(),requested_roots.end(),ordinal))continue;\n  if(ordinal<root_begin')
 # An explicit list never licenses a global completion marker.
 s=s.replace('root_mod==1)gzwrite','root_mod==1 && requested_roots.empty())gzwrite')
 p.write_text(s)
