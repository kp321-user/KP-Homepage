# Python + GitHub + Render Website — Step-by-Step Roadmap

> **Project:** A web app to create and maintain a database that centralizes links to useful information sources (websites, podcasts, YouTube videos, online archives, offline files).

---

## Phase 1 — Plan & Set Up Local Environment

### Step 1 — Install Tools
- Python 3.11+, VS Code, Git, and a GitHub account
- Install required packages:
```bash
pip install flask sqlalchemy requests beautifulsoup4 python-dotenv
```

### Step 2 — Design Your Database Schema
Each "link" record should store:
```
Link: id, url, title, thumbnail, description, type (vid/ebook/webpage),
      source (youtube/website/local), category, date_added, date_published
```

### Step 3 — Choose Your Stack
| Layer | Technology |
|-------|------------|
| Backend | Flask + SQLAlchemy |
| Database (local) | SQLite |
| Database (production) | PostgreSQL on Render |
| Frontend | HTML/CSS + Jinja2 templates |

---

## Phase 2 — Build the Backend (Flask App)

### Step 4 — Create Your Project Structure
```
my-link-db/
├── app.py
├── models.py
├── templates/
│   ├── index.html
│   └── add_link.html
├── static/
│   └── style.css
├── requirements.txt
└── .env
```

### Step 5 — Build the Database Model
Create `models.py` using SQLAlchemy to define the `Link` table with all fields from your schema.

### Step 6 — Build Flask Routes in `app.py`
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Display all links (with filters) |
| `/add` | POST | Add a new link |
| `/delete/<id>` | POST | Remove a link |

### Step 7 — Auto-Fetch Metadata on URL Add
- Use `requests` + `BeautifulSoup` to scrape `<title>` and `og:image` (thumbnail) from any webpage
- For YouTube links, use the **YouTube oEmbed API** (free, no API key needed)

---

## Phase 3 — Build the Frontend

### Step 8 — Create `index.html`
- Display links as cards with: thumbnail, title, source badge, category tag
- Add filter controls:
  - Dropdowns for category, content type, and source
  - Date range picker

### Step 9 — Create `add_link.html`
- Simple form with a URL input field
- Rest of the fields auto-fill from metadata scraping
- Allow manual overrides for category and type

---

## Phase 4 — Push to GitHub

### Step 10 — Initialize Git
```bash
git init
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .
git commit -m "Initial commit"
```

### Step 11 — Create a GitHub Repo and Push
```bash
git remote add origin https://github.com/yourname/my-link-db.git
git push -u origin main
```

---

## Phase 5 — Deploy to Render

### Step 12 — Add Required Files for Render

Create a `Procfile`:
```
web: gunicorn app:app
```

Make sure `requirements.txt` lists all packages:
```
flask
sqlalchemy
requests
beautifulsoup4
python-dotenv
gunicorn
psycopg2-binary
```

### Step 13 — Set Up Render
1. Create a free account at [render.com](https://render.com)
2. **New Web Service** → connect your GitHub repo
3. Add a **PostgreSQL** database (free tier) on Render
4. Set environment variable: `DATABASE_URL` pointing to your Postgres instance
5. Deploy — Render auto-deploys every time you push to GitHub ✅

---

## Phase 6 — Polish & Extras

### Step 14 — Local File Support
- Store `file://` links as-is in the database
- Display a 📄 icon instead of a thumbnail for local files
- Note: These only open correctly on your local machine (browser security limits this)

### Step 15 — Chrome Bookmarks Import *(your open question)*
- In Chrome: **Bookmarks → Bookmark Manager → Export bookmarks** (saves as HTML)
- Write a Python script using `BeautifulSoup` to parse the exported HTML
- Bulk-insert the parsed links into your database
- This is very doable — a great mini-project within the project!

### Step 16 — Future Upgrades to Consider
- Full-text search bar
- Tags in addition to categories
- Browser extension to add links in one click
- Login / authentication to keep it private

---

## Suggested Build Order

```
DB model → Add link (backend) → Display links → Filters → Metadata fetch → Deploy
```

---

## Categories Reference

| Category |
|----------|
| Current Events |
| Historical Documents |
| Entertainment |
| Scientific Research |
| Education (Philosophy, History, IT) |

---

## Content Types & Sources

| Type | Source Examples |
|------|----------------|
| Video | YouTube |
| eBook / PDF | Online archives, local files |
| Webpage | Websites, blogs |
| Podcast | YouTube, podcast platforms |
| Local File | `file:///` paths |