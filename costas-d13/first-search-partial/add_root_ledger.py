from pathlib import Path
p=Path('clique_threaded.cpp');s=p.read_text();needle=' string status=found?"SAT":all?"EXHAUSTED":"TIMEOUT";'
assert needle in s
ledger=r'''
 {ofstream ledger(prefix+".roots.json");ledger<<"{\"generator_status_only\":true,\"order\":"<<n<<",\"target\":"<<target<<",\"jobs\":[";
  for(int k=0;k<(int)jobs.size();k++)ledger<<(k?",":"")<<"{\"ordinal\":"<<k<<",\"catalogue_index\":"<<roots[k]<<",\"complete_negative\":"<<(jobs[k].done?"true":"false")<<",\"nodes\":"<<jobs[k].nodes<<",\"proof\":\""<<jobs[k].file<<"\"}";
  ledger<<"]}\n";}
'''
s=s.replace(needle,ledger+needle);p.write_text(s)
