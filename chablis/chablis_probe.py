"""Chablis source prober. Run where outbound network is open (GitHub Actions, a laptop):

    pip install requests
    python chablis_probe.py seeds.json candidates.json > probe_results.json

seeds.json     [{id, name, test_url}]       known endpoints with a concrete test URL
candidates.json {rows:[{name, url, auth, ...}]}  harvested directory entries (landing pages)

Rules Chablis keeps: public sources only; fetch robots.txt first and treat a disallow as a final
answer (recorded, never routed around); one request per URL; at most one request per second per
host; an honest User-Agent. Output per source: status, content type, bytes, whether it parsed as
JSON/CSV/XML, newest ISO date seen in the body, and the decision taken.
"""
import json, re, sys, time, threading, datetime, urllib.robotparser as rp
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests

UA = 'Chablis/1.0 (public-source probe; contact: owner of this workflow)'
TIMEOUT = 25
_robots, _last, _lock = {}, {}, threading.Lock()
DATE = re.compile(r'(20\d\d)-(\d\d)-(\d\d)')

def allowed(url):
    p = urlparse(url); base = f'{p.scheme}://{p.netloc}'
    with _lock:
        r = _robots.get(base)
    if r is None:
        r = rp.RobotFileParser(); r.set_url(base + '/robots.txt')
        try:
            resp = requests.get(base + '/robots.txt', headers={'User-Agent': UA}, timeout=TIMEOUT)
            if resp.status_code == 200: r.parse(resp.text.splitlines())
            elif resp.status_code in (401, 403): r.disallow_all = True      # denial stands
            else: r.allow_all = True
        except requests.RequestException:
            r.allow_all = True
        with _lock: _robots[base] = r
    return r.can_fetch(UA, url)

def pace(host):
    while True:
        with _lock:
            wait = _last.get(host, 0) + 1.0 - time.time()
            if wait <= 0: _last[host] = time.time(); return
        time.sleep(wait)

def newest_date(text):
    today = datetime.date.today() + datetime.timedelta(days=1)
    best = None
    for y, m, d in DATE.findall(text[:400000]):
        try: dt = datetime.date(int(y), int(m), int(d))
        except ValueError: continue
        if dt <= today and (best is None or dt > best): best = dt
    return best.isoformat() if best else None

def probe(item):
    url = item['test_url']; host = urlparse(url).netloc
    out = {'id': item.get('id'), 'name': item.get('name'), 'url': url, 'probed': datetime.date.today().isoformat()}
    if not allowed(url):
        return {**out, 'result': 'Denied by robots', 'decision': 'recorded, not retried'}
    pace(host)
    try:
        resp = requests.get(url, headers={'User-Agent': UA}, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {**out, 'result': 'Error', 'detail': type(e).__name__}
    ct = resp.headers.get('content-type', '').split(';')[0]
    body = resp.text if resp.status_code == 200 else ''
    fmt = 'other'
    try:
        json.loads(body); fmt = 'JSON'
    except ValueError:
        if body.lstrip().startswith('<?xml') or body.lstrip().startswith('<feed'): fmt = 'XML'
        elif body.count('\n') > 2 and body.count(',') > body.count('\n'): fmt = 'CSV'
        elif body.lstrip().startswith('<'): fmt = 'HTML'
    res = 'Working' if resp.status_code == 200 and body.strip() else 'Error'
    return {**out, 'result': res, 'status': resp.status_code, 'content_type': ct, 'bytes': len(resp.content),
            'format': fmt, 'newest': newest_date(body)}

def main(seeds_path, cand_path):
    items = json.load(open(seeds_path))
    cands = json.load(open(cand_path))['rows']
    for c in cands:
        if c.get('auth') == 'No' and c.get('url', '').startswith('https://'):
            items.append({'id': None, 'name': c['name'], 'test_url': c['url']})
    with ThreadPoolExecutor(16) as ex:
        results = list(ex.map(probe, items))
    json.dump(results, sys.stdout, indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
