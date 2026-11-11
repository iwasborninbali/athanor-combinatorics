from pathlib import Path
p=Path('clique_threaded.cpp');s=p.read_text();assert 'double limitsec;' in s
s=s.replace('double limitsec;','atomic<double> limitsec{0.0};',1)
s=s.replace('  started=common_start;\n  while(!search_stop', '  started=common_start;time_control=prefix+".time-limit";\n  while(!search_stop')
s=s.replace('   if(elapsed()>limitsec){search_stop=true;break;}', '   {ifstream control(time_control);double revised;if(control>>revised && isfinite(revised) && revised>=0)limitsec=revised;}\n   if(elapsed()>limitsec){search_stop=true;break;}')
p.write_text(s)
p=Path('post_partial_search.py');s=p.read_text().replace("subprocess.run(['python3','run_guarded.py','--name',name,'--seconds',str(cap+20)","Path(prefix+'.time-limit').write_text(str(cap)+'\\n')\nsubprocess.run(['python3','run_guarded.py','--name',name,'--seconds',str(min(cap+140,remaining()-180))")
p.write_text(s)
