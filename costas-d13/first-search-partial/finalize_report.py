"""Finalize the research report from checked artifacts, never solver labels alone."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

from check import check
import write_interim

stamp = datetime.now(timezone.utc)
start = datetime(2026, 11, 10, 17, 41, 31, tzinfo=timezone.utc)
target_file = Path('logs/target_resolved.json')
resolution = json.loads(target_file.read_text()) if target_file.exists() else None
continuation = Path('logs/clique_early13.json')
if not continuation.exists():
    continuation = Path('logs/clique_vector13.json')
if not continuation.exists():
    continuation = Path('logs/clique_continue13.json')
search = json.loads(continuation.read_text()) if continuation.exists() else None
text = Path('result.md').read_text()
text = re.sub(r'^# Interim research report.*', '# Research report — '+stamp.strftime('%Y-%m-%d %H:%M UTC'), text, count=1)

if resolution and resolution['kind'] == '12-packing':
    certificate = resolution['certificate']
    audit = check(certificate, 'data/costas_13.txt')
    assert audit['order'] == 13 and audit['size'] == 12
    main = ('**D(13)=12**, using the previously published upper bound. An explicit 12-packing '
            'was independently checked in stdlib Python, including every permutation, all 78 '
            'displacement vectors of each array, and all 156 occupied cells. The lower-bound '
            'witness itself does not require catalogue completeness.')
    target_claim = main
    verification = 'The target witness passed [the independent audit]('+resolution['audit']+').'
    commands = 'python3 check.py '+certificate+' --catalogue data/costas_13.txt'
elif resolution and resolution['kind'] == 'no 12-packing':
    certificate = resolution['certificate']
    audit = json.loads(Path(resolution['audit']).read_text())
    assert audit['verified'] and audit['order'] == 13 and audit['excluded_clique_size'] == 12 and audit['roots'] == 1616
    assert audit['proof_sha256'] == write_interim.sha(certificate)
    assert audit['catalogue_sha256'] == 'a8acc2805c86001250b9104dbf41c2804cdb5734823554ac5313141e9d93e17d'
    main = ('**D(13)=11, conditional on the published catalogue completeness input.** '
            'The complete search excludes 12 pairwise cell-disjoint order-13 Costas arrays. '
            'Its full certificate passed a separate independent verifier. The lower bound '
            '11 is the result already published by Frank–Dinitz.')
    target_claim = (main+' The independent audit checked '+f"{audit['nodes']:,}"+' proof nodes and all 1,616 symmetry roots, '
                    'including the completion marker. See [the full audit]('+resolution['audit']+').')
    py = resolution.get('python_full_audit', '')
    py_guard = Path('logs/python_check13_complete.guard.json')
    if py_guard.exists():
        guard = json.loads(py_guard.read_text())
        if guard['returncode'] != 0 and guard['stop_reason'] == 'finished':
            raise RuntimeError('Unresolved logical disagreement or Python checker failure: inspect logs before claiming a result.')
    if py and Path(py).is_file():
        second = json.loads(Path(py).read_text())
        assert second['verified'] and second['nodes'] == audit['nodes'] and second['proof_sha256'] == audit['proof_sha256']
        verification = 'The entire target trace passed both the independent C++ verifier and the separate stdlib Python verifier.'
    else:
        verification = ('The entire target trace was checked by the independent C++ verifier. '
                        'The separate stdlib Python implementation is provided and was checked on complete smaller cases; '
                        'a full order-13 Python execution was not completed within the remaining wall budget. '
                        'This distinction concerns execution time, not the scope of the completed C++ audit.')
    commands = ('python3 check_clique_proof.py data/costas_13.txt '+certificate+' 12\n\n'
                'clang++ -O3 -std=c++17 check_trace.cpp -lz -o check_trace\n'
                'python3 check_cpp_certificate.py data/costas_13.txt '+certificate+' 12')
    if audit.get('backend') == 'parallel root ranges':
        boundaries = audit['boundaries_file']
        assert audit['boundaries_sha256'] == write_interim.sha(boundaries)
        verification += (' The completed C++ audit used '+str(audit['threads'])+' threads inside one process, with independently enforced root-range coverage and byte alignment.')
        commands = ('python3 check_clique_proof.py data/costas_13.txt '+certificate+' 12\n\n'
                    'clang++ -O3 -std=c++17 '+audit['verifier_source']+' -lz -pthread -o '+Path(audit['verifier_source']).stem+'\n'
                    'python3 check_cpp_certificate.py data/costas_13.txt '+certificate+' 12 --boundaries '+boundaries+' --threads '+str(audit['threads']))
elif resolution and resolution['kind'] == 'chained no 12-packing':
    from check_chained13 import filter_check
    certificate = resolution['certificate']
    first = json.loads(Path(resolution['audit']).read_text())
    second = json.loads(Path(resolution['tail_audit']).read_text())
    k = resolution['prefix_roots']
    relation = filter_check('data/costas_13.txt', resolution['reduced_catalogue'], k)
    assert first['verified'] and first['scope'] == 'specified initial canonical roots only' and first['roots'] == k
    assert second['verified'] and second['order'] == 13 and second['excluded_clique_size'] == 12
    assert second['roots'] == relation['remaining_roots'] and relation['original_roots'] == 1616
    assert first['catalogue_sha256'] == relation['original_catalogue_sha256']
    assert second['catalogue_sha256'] == relation['remaining_catalogue_sha256']
    assert first['proof_sha256'] == write_interim.sha(certificate)
    assert second['proof_sha256'] == write_interim.sha(resolution['tail_certificate'])
    main = ('**D(13)=11, using the published catalogue-completeness input and lower bound 11.** '
            'Two independently checked exclusion certificates cover every possible 12-packing.')
    target_claim = (main+' The first certificate excludes the first '+str(k)+' canonical roots. '
                    'Every hypothetical 12-packing must therefore lie entirely in the induced subgraph on '
                    +str(relation['remaining_vertices'])+' remaining arrays. The reduction was independently checked from the permutations, '
                    'and the second certificate completely excludes 12 in that graph. Together these cover all 1,616 original D4 roots. '
                    'See ['+resolution['audit']+']('+resolution['audit']+'), ['+resolution['tail_audit']+']('+resolution['tail_audit']+') '
                    'and [the independent reduction check]('+resolution['reduction_audit']+').')
    verification = ('Both complete component traces passed independent C++ verification in one process at a time, using three threads. '
                    'The exact induced-subgraph relation was independently checked in stdlib Python. '
                    'The full stdlib Python chain checker is provided; its entire proof traversals were not executed within the wall budget.')
    commands = ('python3 check_chained13.py data/costas_13.txt '+certificate+' '+str(k)+' '+resolution['reduced_catalogue']+' '+resolution['tail_certificate']+'\n\n'
                'clang++ -O3 -std=c++17 check_prefix_parallel.cpp -lz -pthread -o check_prefix_parallel\n'
                './check_prefix_parallel data/costas_13.txt '+certificate+' 12 '+first['boundaries_file']+' 3 '+str(k)+'\n'
                'clang++ -O3 -std=c++17 '+second['verifier_source']+' -lz -pthread -o '+Path(second['verifier_source']).stem+'\n'
                './'+Path(second['verifier_source']).stem+' '+resolution['reduced_catalogue']+' '+resolution['tail_certificate']+' 12 '+second['boundaries_file']+' 3\n'
                'python3 check_chained13.py data/costas_13.txt '+certificate+' '+str(k)+' '+resolution['reduced_catalogue']+' '+resolution['tail_certificate']+' --filter-only')
else:
    main = ('**The programme did not settle D(13). The published interval remains 11 ≤ D(13) ≤ 12.** '
            'No checked 12-witness or independently checked complete order-13 exclusion was obtained.')
    target_claim = main
    verification = 'Only the complete pilot certificates are asserted. Target timeouts and incomplete traces supply no upper bound.'
    commands = ''
    if search:
        target_claim += (' The last combined search reported '+search['status']+', '+f"{search['nodes']:,}"+
                         ' logical nodes and '+str(search['roots'])+' roots entered. This includes the recorded prefix, not a sum of duplicated replay work.')

text = re.sub(r'\*\*The target is not yet settled\..*?\n\n', main+'\n\n', text, count=1, flags=re.S)
text = text.replace('## What is currently established', '## What is established')
marker = '## What is established\n\n'
detail = target_claim[len(main):].lstrip() if target_claim.startswith(main) else target_claim
if detail:
    text = text.replace(marker, marker+detail+'\n\n', 1)
text = text.replace('## Pilots and target trials so far', '## Pilots and target trials')
replacement = ('The search stopped with the scope stated above. '+verification+
               ' Sliced discovery trials were incomplete. No complete target DRAT proof was produced; incomplete DRAT files were hashed and removed.')
text = re.sub(r'The 1,500-second trace is being continued\..*?\n\n', replacement+'\n\n', text, count=1, flags=re.S)
if search:
    row = ('| Continued order-13 search | '+search['status']+'; '+f"{search['nodes']:,}"+' logical nodes | '+f"{search['seconds']:.1f}"+' s in continuation stage |')
    anchor = '| Order 13, complete clique trial | TIMEOUT: 110,379,008 nodes; sixth root unfinished | 1,500 s |'
    stages = []
    for filename, label in [('logs/clique_continue13.json', 'First order-13 continuation'),
                            ('logs/clique_vector13.json', 'Aborted representation-only replay')]:
        if Path(filename).exists():
            stage = json.loads(Path(filename).read_text())
            stages.append('| '+label+' | '+stage['status']+'; '+f"{stage['nodes']:,}"+' logical states reached, '
                          +f"{stage.get('replayed_nodes',0):,}"+' replayed | '+f"{stage['seconds']:.1f}"+' s |')
    text = text.replace(anchor, anchor+'\n'+'\n'.join(stages+[row]))

reduced_trial = Path('logs/reduced_target13.json')
if reduced_trial.exists():
    rt = json.loads(reduced_trial.read_text())
    summary = ('The final reduced-graph trial used '+str(rt.get('threads',1))+' threads in one process and reported '
               +rt['status']+' after '+f"{rt['nodes']:,}"+' search nodes and '+f"{rt['seconds']:.3f}"+' seconds. '
               'Its generator flags alone do not establish an exclusion.')
    text = text.replace('## Pilots and target trials\n\n','## Pilots and target trials\n\n'+summary+'\n\n',1)

if resolution:
    hash_value = write_interim.sha(resolution['certificate'])
    row = '| ['+resolution['certificate']+']('+resolution['certificate']+') | `'+hash_value+'` |'
    if resolution['kind'] == 'no 12-packing' and audit.get('boundaries_file'):
        boundary_file = audit['boundaries_file']
        row += '\n| ['+boundary_file+']('+boundary_file+') | `'+write_interim.sha(boundary_file)+'` |'
    if resolution['kind'] == 'chained no 12-packing':
        for artifact in (resolution['tail_certificate'], first['boundaries_file'], second['boundaries_file'], resolution['reduced_catalogue']):
            row += '\n| ['+artifact+']('+artifact+') | `'+write_interim.sha(artifact)+'` |'
    at = text.index('\nAll certificate files and hashes')
    text = text[:at].rstrip()+'\n'+row+'\n'+text[at:]
    text = text.replace('## Certificates and independent checkers\n\n',
                        '## Certificates and independent checkers\n\n'+verification+'\n\nTarget check commands:\n\n```sh\n'+commands+'\n```\n\n', 1)
    not_established = ('The historical catalogue enumeration was not independently repeated. Exact values at orders 14, 15 and 17 '
                       'were not determined here; only the previously known 12-packings at 14 and 17 were reproduced. '
                       'No enumeration of all maximum or maximal packings is claimed. '+verification)
else:
    not_established = ('D(13) remains undecided. No new bound is claimed at orders 13, 14, 15 or 17. '
                       'No historical catalogue enumeration was repeated. A complete search result requires completion '
                       'and independent checking of all cases; neither heuristic maxima nor timeouts suffice.')
partial_file = Path('logs/partial_reduction13.json')
if not resolution and partial_file.exists():
    partial = json.loads(partial_file.read_text())
    audit = json.loads(Path(partial['audit']).read_text())
    assert audit['verified'] and audit['scope'] == 'specified initial canonical roots only'
    assert audit['proof_sha256'] == write_interim.sha(partial['certificate'])
    paragraph = ('A restricted order-13 exclusion was independently checked: the first '
                 +str(audit['roots'])+' canonical roots, through original catalogue representative index '
                 +str(audit['last_root_catalogue_index'])+', containing '+f"{audit['nodes']:,}"
                 +' trace nodes. Consequently every hypothetical 12-packing lies entirely in the induced subgraph on the '
                 +f"{partial['remaining_vertices']:,}"+' arrays whose representative index is larger. This removes '
                 +str(partial['removed_vertices'])+' vertices, but supplies no new global bound. See ['
                 +partial['audit']+']('+partial['audit']+') and [the explicit reduction](logs/partial_reduction13.json).')
    text = text.replace('## What is established\n\n', '## What is established\n\n'+paragraph+'\n\n', 1)
    reduced_file = partial['remaining_catalogue']
    relation_file = Path('logs/reduction13_independent_check.json')
    if relation_file.exists():
        relation = json.loads(relation_file.read_text())
        assert relation['verified'] and relation['remaining_catalogue_sha256'] == write_interim.sha(reduced_file)
        reduction_note = ('The exact reduced catalogue ['+reduced_file+']('+reduced_file+') has SHA-256 `'+write_interim.sha(reduced_file)+'`. Its relation to the full input was independently checked in stdlib Python: [audit](logs/reduction13_independent_check.json).')
        text = text.replace('## Certificates and independent checkers\n\n', '## Certificates and independent checkers\n\n'+reduction_note+'\n\n', 1)
    command = ('python3 check_clique_prefix.py data/costas_13.txt '+partial['certificate']+' 12 '+str(audit['roots'])+'\n'
               'clang++ -O3 -std=c++17 check_root_prefix.cpp -lz -o check_root_prefix\n'
               './check_root_prefix data/costas_13.txt '+partial['certificate']+' 12 '+str(audit['roots']))
    paragraph += (' The restricted trace was fully checked in the independent C++ implementation; '
                  'the stdlib Python implementation was exercised on smaller restricted cases. Check commands:\n\n```sh\n'
                  +command+'\n```\n\nCertificate SHA-256: `'+audit['proof_sha256']+'`.')
    text = text.replace('## Certificates and independent checkers\n\n', '## Certificates and independent checkers\n\n'+paragraph+'\n\n', 1)
    if audit.get('boundaries_file'):
        text = text.replace('Certificate SHA-256: `'+audit['proof_sha256']+'`.', 'Certificate SHA-256: `'+audit['proof_sha256']+'`. Parallel range index: ['+audit['boundaries_file']+']('+audit['boundaries_file']+'), SHA-256 `'+audit['boundaries_sha256']+'`. The actual audit used '+str(audit['threads'])+' threads in one process; the displayed serial and Python commands check the same restricted roots without this index.')
    not_established += ' The root cases beyond the final checked reduction remain open.'
    text = text.replace('Only the complete pilot certificates are asserted. Target timeouts and incomplete traces supply no upper bound.', 'The complete pilot certificates and the explicitly restricted root exclusions are asserted. Target timeouts supply no global upper bound.')

text = re.sub(r'## What is not established\n\n.*?\n\n## Prior art',
              '## What is not established\n\n'+not_established+'\n\n## Prior art', text, count=1, flags=re.S)
extended_file = Path('logs/extended_partial_reduction13.json')
if not resolution and extended_file.exists():
    from check_chained13 import filter_check
    extension = json.loads(extended_file.read_text())
    extra = json.loads(Path(extension['audit']).read_text())
    assert extra['verified'] and extra['scope'] == 'specified initial canonical roots only'
    assert extra['order'] == 13 and extra['excluded_size_in_these_roots'] == 12
    assert extra['proof_sha256'] == write_interim.sha(extension['certificate'])
    combined = extension['combined_original_initial_roots']
    checked_relation = filter_check('data/costas_13.txt', extension['remaining_catalogue'], combined)
    assert checked_relation['remaining_catalogue_sha256'] == extension['remaining_catalogue_sha256']
    paragraph = ('A further independent audit excludes the first '+str(extra['roots'])+' roots of the reduced graph, with '
                 +f"{extra['nodes']:,}"+' proof nodes. Together the two scoped certificates exclude the first '
                 +str(combined)+' canonical root families of the original graph. Every hypothetical 12-packing must lie entirely in ['
                 +extension['remaining_catalogue']+']('+extension['remaining_catalogue']+'), containing '
                 +f"{extension['remaining_vertices']:,}"+' arrays. The exact combined filter was checked again in stdlib Python. '
                 'This is a further certified reduction; D(13) remains 11–12. See [the second audit]('
                 +extension['audit']+') and [the combined reduction](logs/extended_partial_reduction13.json).')
    text = text.replace('## What is established\n\n', '## What is established\n\n'+paragraph+'\n\n', 1)
    artifacts = [extension['certificate'],extra['boundaries_file'],extension['remaining_catalogue']]
    rows = '\n'.join('| ['+f+']('+f+') | `'+write_interim.sha(f)+'` |' for f in artifacts)
    commands = ('python3 check_clique_prefix.py '+extension['input_catalogue']+' '+extension['certificate']+' 12 '+str(extra['roots'])+'\n'
                'clang++ -O3 -std=c++17 check_prefix_parallel_stack.cpp -lz -pthread -o check_prefix_parallel_stack\n'
                './check_prefix_parallel_stack '+extension['input_catalogue']+' '+extension['certificate']+' 12 '+extra['boundaries_file']+' 3 '+str(extra['roots'])+'\n'
                'python3 check_chained13.py data/costas_13.txt - '+str(combined)+' '+extension['remaining_catalogue']+' - --filter-only')
    section = (paragraph+'\n\nThe final command checks only the data filter; the two proof traversals have the separate commands given here and below. '
               'The second proof was fully checked by C++; full Python execution of these large prefixes was not completed.\n\n'
               '```sh\n'+commands+'\n```\n\n| Additional artifact | SHA-256 |\n|---|---|\n'+rows+'\n\n')
    text = text.replace('## Certificates and independent checkers\n\n','## Certificates and independent checkers\n\n'+section,1)
    text = text.replace('The root cases beyond the final checked reduction remain open.',
                        'The cases after the first '+str(combined)+' original canonical roots remain open; no global upper bound was obtained.')

elapsed = (stamp-start).total_seconds()
text = text.replace('Current execution state is also recorded in [next.md](next.md).',
                    'Final report time: '+stamp.strftime('%Y-%m-%d %H:%M:%S UTC')+f'; elapsed {elapsed/3600:.3f} hours. Execution records are in [progress.md](progress.md).')
draft = '--draft' in sys.argv
if draft:
    text = text.replace('# Research report', '# Draft research report', 1)
Path('result-draft.md' if draft else 'result.md').write_text(text)
Path('logs/draft_report_status.json' if draft else 'logs/final_report_status.json').write_text(json.dumps({'utc': stamp.isoformat(), 'elapsed_seconds': elapsed,
    'resolution': resolution, 'search': search}, indent=2)+'\n')
print(main)
