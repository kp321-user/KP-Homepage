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
- `RENDER_DATABASE_URL` — needed only to run the sync scripts (`one_way_push_db.py` / `two_way_sync_db.py`)
- `RENDER` — set to any value on Render; used to hide admin UI from public visitors
- `YOUTUBE_COOKIES` — YouTube cookies as base64, set on Render; required for bot-protected videos

## Syncing local DB to Render
```
python one_way_push_db.py
```
Pushes local SQLite to Render PostgreSQL. This is the main sync script. `two_way_sync_db.py` exists as a backup (bidirectional, newer `last_modified` wins). Both require `RENDER_DATABASE_URL` in `.env`.

## Slug logic (md_files → DB)
Filename `01_foo_bar.md` → strip first 3 chars → remove `.md` → replace `_` with `-` → lowercase → `foo-bar`. Also tries appending `-overview` if no direct match.

## Key models
Both models are independent — no foreign keys or SQLAlchemy relationships between them.

- `Link` — url, title, thumbnail, category, type, date_added, last_modified
- `HistoryPage` — title, slug (unique), era, period, phase, start_year, content (markdown), date_added, last_modified

## Templates
- `history_pages/obsolete_htmls/` — old static HTML files, superseded by DB-driven `view_hpage.html`
- History articles are stored as markdown in the DB and rendered at `/hpages/<slug>`

## Deployment
Render auto-deploys from `main` branch on GitHub push. Build command in Render dashboard is `./build.sh`, which installs `ffmpeg` (required by the converter page) and runs `pip install -r requirements.txt`. `Procfile` tells Render to serve the app with gunicorn (`web: gunicorn app:app`).

## Key files
- `app.py` — main Flask app, all routes
- `templates/` — Jinja2 HTML templates
- `md_files/` — source markdown for history articles
- `build.sh` — Render build script; installs ffmpeg and Python deps
- `Procfile` — tells Render to serve with gunicorn
- `one_way_push_db.py` — main script to push local DB to Render (use this)
- `two_way_sync_db.py` — backup bidirectional sync script
- `extract_document.py` — uses Claude vision API to extract structured data from document images
- `history_periods.py` — defines the era/period/phase taxonomy used by history page filters
- `md_files/migrate_md.py` — bulk-writes markdown from `md_files/` into the DB (see Slug logic section)

## Routes
| Route | Auth | Description |
|---|---|---|
| `/` | No | Home page |
| `/links` | No | Links page (filterable by category/type) |
| `/add-link` | Yes | Add a new link |
| `/edit-link/<id>` | Yes | Edit a link |
| `/delete-link/<id>` | Yes | Delete a link |
| `/history` | No | History articles list (filterable, sortable) |
| `/hpages/<slug>` | No | View a history article |
| `/add-hpage` | Yes | Add a history article |
| `/edit-hpage/<id>` | Yes | Edit a history article |
| `/delete-hpage/<id>` | Yes | Delete a history article |
| `/converter` | Yes | YouTube download page (mp3/mp4) |
| `/login` `/logout` | — | Auth |

## Notes pages
Static template pages served at fixed routes — no DB involvement:
- `/python_notes`, `/github_notes`, `/beautifulsoup_notes`, `/llms`, `/java-notes`

Generated with Pandoc from source documents. To regenerate, convert the source file with Pandoc and drop the output into `templates/`.

## Known issues
- Converter page (YouTube download) is live on Render. Some videos trigger bot detection due to datacenter IP — no fix short of residential proxies. YouTube cookies stored as base64 in `YOUTUBE_COOKIES` env var on Render.
- `/pick-folder` uses tkinter to open a GUI folder picker — only works locally. The converter template hides it on Render.

## Current active work
- Nothing in progress