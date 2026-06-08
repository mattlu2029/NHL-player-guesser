import json, urllib.request, time, datetime
from collections import Counter

OUT = "C:/Users/mattl/nhl-player-guess/build"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get(u, tries=4):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=HEADERS), timeout=20) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(0.5 * (i + 1))
    raise last

# reuse cached team histories (keyed by player id) so we don't re-fetch ~700 landings
old = json.load(open(OUT + "/players.json", encoding="utf-8"))
hist = {p['id']: p.get('history') for p in old['players']}

def spec_pos(code, hand):
    # NHL API only reports 'D' for defense; derive side from handedness (standard convention)
    if code == 'D':
        return 'RD' if hand == 'R' else 'LD'
    return {'C': 'C', 'L': 'LW', 'R': 'RW', 'G': 'G'}.get(code, 'C')

s = get("https://api-web.nhle.com/v1/standings/now")
abbrevs = sorted({r['teamAbbrev']['default'] for r in s['standings']})

players = {}
for ab in abbrevs:
    ro = get("https://api-web.nhle.com/v1/roster/%s/current" % ab)
    for grp in ('forwards', 'defensemen', 'goalies'):
        for p in ro.get(grp, []):
            hand = p.get('shootsCatches') or ''
            if not p.get('birthDate') or p.get('sweaterNumber') is None or not hand:
                continue
            pid = p['id']
            h = hist.get(pid) or [ab]
            if ab not in h:
                h = h + [ab]
            players[pid] = {
                'id': pid,
                'name': p['firstName']['default'] + ' ' + p['lastName']['default'],
                'team': ab,
                'pos': spec_pos(p.get('positionCode'), hand),
                'hand': hand,
                'birth': p.get('birthDate'),
                'num': p.get('sweaterNumber'),
                'history': h,
            }

final = sorted(players.values(), key=lambda x: x['name'])
meta = {'generated': datetime.date.today().isoformat(), 'count': len(final), 'players': final}
with open(OUT + "/players.json", "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False)
print("count", len(final), "| pos dist", dict(sorted(Counter(p['pos'] for p in final).items())))
