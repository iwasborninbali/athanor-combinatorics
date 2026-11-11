"""Save public, unauthenticated prior-art responses; no paid services."""
import json
import pathlib
import urllib.request
import urllib.parse
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent / 'sources'
ROOT.mkdir(exist_ok=True)
QUERIES = {
    'openalex_title': 'https://api.openalex.org/works?' + urllib.parse.urlencode({'filter': 'title.search:Small Bipancyclic Graphs', 'per-page': 50}),
    'openalex_topic': 'https://api.openalex.org/works?' + urllib.parse.urlencode({'search': 'bipancyclic', 'per-page': 100}),
    'openalex_book': 'https://api.openalex.org/works/https://doi.org/10.1007/978-3-319-31951-3',
    'openalex_actual_book_citers': 'https://api.openalex.org/works?' + urllib.parse.urlencode({'filter': 'cites:W2489747349', 'per-page': 100}),
    'oeis_bipancyclic': 'https://oeis.org/search?' + urllib.parse.urlencode({'q': 'bipancyclic', 'fmt': 'json'}),
    'unique2016': 'https://webhome.auburn.edu/~zww0009/UBPCG.v4.pdf',
}

if __name__ == '__main__':
    for name, url in QUERIES.items():
        log = {'name': name, 'url': url, 'utc': datetime.now(timezone.utc).isoformat()}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research source check)'})
            with urllib.request.urlopen(req, timeout=25) as response:
                data = response.read(5000000)
                log.update(status=response.status, content_type=response.headers.get('Content-Type'))
            suffix = '.pdf' if data.startswith(b'%PDF') else '.json'
            (ROOT / (name + suffix)).write_bytes(data)
            log['bytes'] = len(data)
        except Exception as exc:
            log['error'] = str(exc)
        with (ROOT / 'access.jsonl').open('a') as out:
            out.write(json.dumps(log) + '\n')
        print(json.dumps(log), flush=True)
