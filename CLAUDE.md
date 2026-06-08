# Link-DB Project

Flask web app serving a personal homepage with links, history articles, and notes pages.

## Stack
- **Backend:** Flask + SQLAlchemy
- **Local DB:** SQLite at `instance/kp_db_2026.db`
- **Production DB:** PostgreSQL on Render (env var `DATABASE_URL`)
- **Auth:** Single hardcoded user via `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars

## Running locally
```
python app.py
```
Runs in debug mode on http://127.0.0.1:5000

## Environment variables required
- `SECRET_KEY` — Flask secret key
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — login credentials
- `DATABASE_URL` — set automatically by Render in production; omit locally to use SQLite
- `RENDER_DATABASE_URL` — needed only to run `sync_db.py`
- `RENDER` — set to any value on Render; used to hide admin UI from public visitors

## Syncing local DB to Render
```
python sync_db.py
```
Bidirectional sync between local SQLite and Render PostgreSQL. Requires `RENDER_DATABASE_URL` in `.env`. Newer `last_modified` timestamp wins.

## Slug logic (md_files → DB)
Filename `01_foo_bar.md` → strip first 3 chars → remove `.md` → replace `_` with `-` → lowercase → `foo-bar`. Also tries appending `-overview` if no direct match.

## Key models
- `Link` — url, title, thumbnail, category, type, date_added, last_modified
- `HistoryPage` — title, slug, era, period, phase, start_year, content (markdown), date_added, last_modified

## Templates
- `history_pages/obsolete_htmls/` — old static HTML files, superseded by DB-driven `view_hpage.html`
- History articles are stored as markdown in the DB and rendered at `/hpages/<slug>`

## Deployment
Render auto-deploys from `main` branch on GitHub push.

## Key files
- `app.py` — main Flask app, all routes
- `sync_db.py` — bidirectional SQLite/PostgreSQL sync
- `templates/` — Jinja2 HTML templates
- `md_files/` — source markdown for history articles

## Known issues
- YouTube-to-MP3 route must NEVER be pushed to Render

## Current active work
- Nothing in progress