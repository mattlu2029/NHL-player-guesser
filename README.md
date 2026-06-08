# 🏒 NHL Player Guess

A Wordle-style guessing game for active NHL players. Guess the secret player in 10 tries; after each guess you get five clues.

**Play:** open `index.html` in any browser (it's a single self-contained file — no install, works offline).

## Clues
| Clue | 🟩 Green | 🟨 Yellow | ⬛ Blank |
|------|---------|-----------|----------|
| **Team** | plays there now | played there before | never |
| **Division** | same division | same conference | neither |
| **Position** (C/LW/RW/LD/RD/G) | exact | same type (both F / both D) | no match |
| **Age** | exact | — | ▲ older / ▼ younger |
| **Jersey No.** | exact | — | ▲ higher / ▼ lower |

> Note: the NHL API only reports "D" for defense, so left/right defense (LD/RD) is derived from handedness (shoots L → LD, shoots R → RD).

## Modes
- **📅 Daily Challenge** — one secret player per day, the same for everyone, flips at 12:00 AM PT.
- **🎲 Random Player** — a random active player to guess.
- **🧑‍🤝‍🧑 Pass to a Friend** — pick the secret player, then hand the device over.

## Stats
Stats (played, win %, daily streak, guess distribution) are saved in your browser. With an optional Supabase backend you also get accounts (email code or Google sign-in) and a cross-device leaderboard.

## Data
Player data is pulled live from the public NHL API (`api-web.nhle.com`) — 872 active players across all 32 teams, including team history (for the yellow "former team" clue). Ages are computed from birthdates so they never go stale.

## Configuration (optional)
Both are near the top of the `<script>` in `index.html`:
- `DAILY_URL` — a JSON file you control (e.g. a GitHub Gist raw URL) mapping dates to players for the Daily Challenge.
- `SUPABASE_URL` / `SUPABASE_ANON_KEY` — enable accounts + leaderboard (see `supabase-setup.sql`).

## Rebuilding the player data
```bash
cd build
python build_data.py          # fetch fresh rosters + team histories -> players.json
python -c "t=open('index_template.html',encoding='utf-8').read(); d=open('players.json',encoding='utf-8').read(); open('../index.html','w',encoding='utf-8').write(t.replace('__NHL_DATA__',d))"
```

## Project layout
```
index.html              the game (data embedded)
daily.example.json      template for the Daily Challenge schedule
supabase-setup.sql      DB schema + row-level-security for stats/leaderboard
build/
  build_data.py         fetch rosters + histories from the NHL API
  patch_positions.py    refresh rosters / specific positions, reuse cached histories
  index_template.html   the game with a __NHL_DATA__ placeholder
  players.json          generated player dataset
```
