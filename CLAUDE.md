# Working notes (for Claude)

## Auto-deploy workflow — do this without asking
After **any** change to the game:
1. If `build/index_template.html` was edited, **regenerate `index.html`** (the live site serves `index.html`, which is generated — never ship template-only edits):
   ```bash
   cd build && python -c "t=open('index_template.html',encoding='utf-8').read(); d=open('players.json',encoding='utf-8').read(); open('../index.html','w',encoding='utf-8').write(t.replace('__NHL_DATA__',d))"
   ```
2. `git add -A && git commit && git push` automatically (the user has standing approval to auto-push).
3. End commit messages with: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`

## Hosting
- Live site: https://nhl-player-guesser.vercel.app/ — Vercel auto-deploys on push to `main`.
- `index.html` is a single self-contained file with player data embedded.

## Source of truth
- Edit `build/index_template.html` (contains the `__NHL_DATA__` placeholder), then regenerate `index.html`.
- Player data: `build/players.json` (rebuild via `build/build_data.py` or `build/patch_positions.py`).
