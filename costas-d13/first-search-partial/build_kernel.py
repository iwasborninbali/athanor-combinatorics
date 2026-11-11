from pathlib import Path
s=Path('clique.cpp').read_text()
start=s.index('bool expand(Bits p){\n ++nodes;')
end=s.index(' int need=target-(int)path.size();',start)
admin=s[start:end].replace('bool expand(Bits p){','bool enter_node(){')+' return true;\n}\n'
# The old administrative false return stops a node; true permits processing it.
s=s[:start]+admin+'\n#ifdef ENABLE_SMALL_KERNEL\n#include "small_kernel.hpp"\n#endif\n\nbool expand(Bits p){\n#ifdef ENABLE_SMALL_KERNEL\n if(pop(p)<=128){SmallKernel kernel(p);return kernel.expand(kernel.initial);}\n#endif\n if(!enter_node())return false;\n'+s[end:]
Path('clique_kernel.cpp').write_text(s)
