import json, urllib.request, time, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "C:/Users/mattl/nhl-player-guess/build"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get(u, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(0.5 * (i + 1))
    raise last

# 1) team list + full-name -> abbrev map
s = get("https://api-web.nhle.com/v1/standings/now")
abbrevs = sorted({r['teamAbbrev']['default'] for r in s['standings']})
name2abbr = {}
for r in s['standings']:
    ab = r['teamAbbrev']['default']
    name2abbr[r['teamName']['default']] = ab
    name2abbr[r['teamCommonName']['default']] = ab
# recent relocation so franchise history resolves intuitively
for k in ("Arizona Coyotes", "Phoenix Coyotes", "Coyotes"):
    name2abbr[k] = "UTA"
print("teams:", len(abbrevs), abbrevs, flush=True)

POS = {'C': 'F', 'L': 'F', 'R': 'F', 'D': 'D', 'G': 'G'}

# 2) current rosters -> core attributes
players = {}
for ab in abbrevs:
    try:
        ro = get("https://api-web.nhle.com/v1/roster/%s/current" % ab)
    except Exception as e:
        print("ROSTER FAIL", ab, e, flush=True)
        continue
    for grp in ('forwards', 'defensemen', 'goalies'):
        for p in ro.get(grp, []):
            pid = p['id']
            players[pid] = {
                'id': pid,
                'name': (p['firstName']['default'] + ' ' + p['lastName']['default']),
                'team': ab,
                'pos': POS.get(p.get('positionCode'), 'F'),
                'hand': p.get('shootsCatches') or '',
                'birth': p.get('birthDate'),
                'num': p.get('sweaterNumber'),
            }
print("rostered players:", len(players), flush=True)

# 3) team history per player via landing endpoint (threaded)
def hist(pid):
    try:
        d = get("https://api-web.nhle.com/v1/player/%d/landing" % pid)
        out = set()
        for r in d.get('seasonTotals', []):
            if r.get('leagueAbbrev') != 'NHL':
                continue
            nm = (r.get('teamName') or {}).get('default') or (r.get('teamCommonName') or {}).get('default')
            ab = name2abbr.get(nm)
            if ab:
                out.add(ab)
        return pid, sorted(out)
    except Exception:
        return pid, None

ids = list(players)
done = 0
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(hist, i): i for i in ids}
    for f in as_completed(futs):
        pid, h = f.result()
        cur = players[pid]['team']
        if not h:
            h = [cur]
        if cur not in h:
            h = h + [cur]
        players[pid]['history'] = h
        done += 1
        if done % 75 == 0:
            print("history %d/%d" % (done, len(ids)), flush=True)

# 4) finalize: keep players with the fields the clues need
final, skipped = [], 0
for p in players.values():
    if not p['birth'] or p['num'] is None or not p['hand']:
        skipped += 1
        continue
    final.append(p)
final.sort(key=lambda x: x['name'])

meta = {
    'generated': datetime.date.today().isoformat(),
    'count': len(final),
    'players': final,
}
with open(OUT + "/players.json", "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False)
print("DONE wrote %d players (skipped %d missing fields)" % (len(final), skipped), flush=True)
