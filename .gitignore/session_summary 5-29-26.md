# Link Database App — Session Summary & Next Steps

## What We Built
A Flask web app that stores and displays a database of useful links.

---

## Current File Structure
```
link-db/
├── instance/
│   └── links.db          ← SQLite database (auto-created)
├── static/
│   └── darkstyle.css     ← Dark theme CSS
├── templates/
│   ├── index.html        ← Homepage displaying all links
│   └── add_link.html     ← Form to add new links
├── app.py                ← Main Flask app
├── .env                  ← Secret keys (not on GitHub)
└── requirements.txt      ← Python packages
```

---

## What's Working
- ✅ Flask app with SQLAlchemy database (SQLite locally)
- ✅ Link model with: `id`, `url`, `title`, `thumbnail`, `category`, `type`, `date_added`
- ✅ Homepage displays all links sorted by date (newest first)
- ✅ Add link form at `/add`
- ✅ Auto-fetches title and thumbnail (`og:image`) when URL is entered
- ✅ Delete button on each link item
- ✅ Thumbnail icon displayed left of each link, links to URL
- ✅ Auto-adds `https://` if user forgets
- ✅ Dark styled CSS with tight compact layout

---

## Current app.py Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Display all links |
| `/add` | GET/POST | Show form / save new link |
| `/delete/<id>` | POST | Remove a link |
| `/fetch-metadata` | POST | Auto-fetch title and thumbnail from URL |

---

## Stack
| Layer | Technology |
|-------|-----------|
| Backend | Flask + Flask-SQLAlchemy |
| Database (local) | SQLite |
| Database (production) | PostgreSQL on Render |
| Frontend | HTML + CSS + Jinja2 |
| Metadata scraping | requests + BeautifulSoup4 |

---

## Next Steps

### Step 1 — Filters (almost done, needs wiring in)
Add dropdowns to homepage to filter links by category and type:
- Update `index` route in `app.py` to accept `?category=` and `?type=` query params
- Add filter dropdowns to `index.html` that auto-submit on change
- Add "Clear Filters" link

### Step 2 — Push to GitHub
```bash
git init
echo "instance/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/kp321-user/link-db.git
git push -u origin main
```

### Step 3 — Deploy to Render
- Create `requirements.txt` with all packages
- Add `Procfile`: `web: gunicorn app:app`
- Create Render account, connect GitHub repo
- Add PostgreSQL database on Render
- Set `DATABASE_URL` environment variable
- Switch `app.py` to use `DATABASE_URL` for production

### Step 4 — Future Improvements
- Search bar (full text search across titles and URLs)
- Edit existing links
- Chrome bookmarks import (parse exported HTML file with BeautifulSoup)
- Tags in addition to categories
- Pagination for large lists

---

## Packages Required
```
flask
flask-sqlalchemy
requests
beautifulsoup4
python-dotenv
gunicorn
psycopg2-binary
```

---

## Key Concepts Covered Today
- Flask routes (`GET` vs `POST`)
- SQLAlchemy models and database sessions
- Jinja2 templating (`{% for %}`, `{% if %}`, `{{ }}`)
- CSS specificity and the box model
- BeautifulSoup metadata scraping
- URI structure (`sqlite:///`, `postgresql://`)
- `db.create_all()` and when to delete/recreate the database
