# Draft Assistant (Sleeper + FantasyPros) — Codespaces Ready

A local-first virtual draft assistant optimized for **GitHub Codespaces**.  
It pulls **real datasets at runtime** from free/public sources (FantasyPros ECR/tiers + ADP, Sleeper players list; optional Best Ball ADP) and syncs them into a SQLite core DB. It serves a local React UI with a FastAPI backend.

> **TL;DR:** Open in Codespaces, wait for setup to finish, then run: `./scripts/dev.sh`  
> Frontend: http://localhost:5173 · Backend: http://localhost:8000/docs

## Features (from spec)
- Core Data: FantasyPros **ECR + tiers** (Half PPR overall) and **Half-PPR ADP** (consensus from multiple hosts). Optional Best Ball ADP as Underdog proxy.
- Sleeper `player_id` as primary key with crosswalk to names/positions/teams.
- Draft Board: manual pick logging (in-person draft), **undo/redo** (undone picks removed).
- Suggestions: 2–3 top picks + 5–10 highlights. Live sliders: Value / Tier / Roster Needs / BPA.
- Live cues: positional scarcity, bye-week conflicts, stack opportunities, injury risk, reach/steal.
- Opponents: team names + roster needs; simple run prediction.
- Refresh: on open + manual; Quiet Mode; 10m TTL (news 60–90s).
- Exports: CSV/Excel draft board & picks; optional PDF board.
- Local-only credentials (encrypted) with easy future paid-source add-ons.
- **Excel sync** stubs included; first release focuses on fast local UI + CSV export.

## Real data sources (fetched on refresh)
- FantasyPros **Half-PPR Overall Cheat Sheet** (ECR + tiers)  
- FantasyPros **Half-PPR ADP** (consensus)  
- FantasyPros **Best Ball ADP** (optional as Underdog proxy)  
- Sleeper **Players** dataset (for IDs + metadata)

These are fetched via HTTP during setup/refresh and normalized into SQLite.  
If a site structure changes, the ingestor logs a warning but the app still runs.

## Quick Start (GitHub Codespaces)
1. Click **Code → Codespaces → Create codespace on main**.
2. Wait for the post-create to finish (Python+Node deps installed).
3. Start both servers:
   ```bash
   ./scripts/dev.sh
   ```
4. Open the forwarded ports:
   - Frontend: 5173
   - Backend: 8000

## Local dev (non-Codespaces)
- Prereqs: Python 3.11+, Node 20+
- Backend:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn backend.app:app --reload --port 8000
  ```
- Frontend:
  ```bash
  cd frontend
  npm i
  npm run dev
  ```

## Project Structure
```
backend/
  app.py              # FastAPI app + routes
  db.py               # SQLite engine + session + create_all
  models.py           # SQLAlchemy ORM models
  schemas.py          # Pydantic response/request models
  ingest/
    fantasypros.py    # FantasyPros ECR + tiers + ADP (real fetch)
    sleeper.py        # Sleeper players (real fetch)
    news_free.py      # Basic news scraping (lightweight)
    injuries_free.py  # Simple injury risk (news signal + age/pos)
  services/
    ranking_blend.py  # Blended rank calc + tier overrides
    suggestions.py    # 2–3 suggested, 5–10 highlight list
    opponents.py      # Team roster needs + run prediction
    exports.py        # CSV/Excel export helpers
  utils/
    settings.py       # Config & weights
    excel_io.py       # (stub) Excel sync (write-only first release)
    cache.py          # TTL cache helpers
frontend/
  (React + Vite + TS) Draft Room UI
.devcontainer/
  devcontainer.json + Dockerfile (Python+Node)
scripts/
  setup.sh            # Codespaces postCreate
  dev.sh              # Run backend+frontend concurrently
assets/
  (placeholder templates if needed later)
data/
  draft.db (created at runtime)
requirements.txt
```

## Legal / Fair Use
This tool fetches public pages for personal draft assistance (non-commercial). It respects source rate-limits and caches results. You are responsible for complying with each site's terms.

## Roadmap
- Add paid sources (DraftSharks injuries, Rotowire news, PFF metrics) via local encrypted keys.
- Snapshot Core → Excel at draft start; full Excel read/write sync.
- Opponent simulation w/ historical drafts import.
- Printable PDF Board.
