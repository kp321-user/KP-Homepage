import os
import markdown
from flask import Flask, redirect, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import threading
from flask import send_file
import yt_dlp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

database_url = os.environ.get("DATABASE_URL", "sqlite:///links.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# ── Single user from environment ──
class User(UserMixin):
    id = 1
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "password")


@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == 1:
        return User()
    return None


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    title = db.Column(db.String(200))
    thumbnail = db.Column(db.String(500))
    category = db.Column(db.String(100))
    type = db.Column(db.String(50))
    date_added = db.Column(db.DateTime)
    last_modified = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class HistoryPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    period = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_modified = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


with app.app_context():
    db.create_all()
    print("Created at:", os.path.abspath("links.db"))


@app.route("/")
def home():
    return render_template("home.html", render_env=os.getenv("RENDER"))


@app.route("/python_notes")
def python_notes():
    return render_template("python_notes.html")


@app.route("/history")
def history():
    import re

    sort = request.args.get("sort", "date_added")
    selected_period = request.args.get("period", "")

    query = HistoryPage.query
    if selected_period:
        query = query.filter_by(period=selected_period)

    if sort == "title":
        pages = query.order_by(HistoryPage.title.asc()).all()
    elif sort == "last_modified":
        pages = query.order_by(HistoryPage.last_modified.desc()).all()
    else:
        pages = query.order_by(HistoryPage.date_added.desc()).all()

    def period_sort_key(period):
        if period:
            match = re.search(r"\d+", period)
            if match:
                return int(match.group())
        return 9999

    periods = [
        r[0] for r in db.session.query(HistoryPage.period).distinct().all() if r[0]
    ]
    periods.sort(key=period_sort_key)

    return render_template(
        "history.html",
        render_env=os.getenv("RENDER"),
        history_pages=pages,
        selected_sort=sort,
        selected_period=selected_period,
        periods=periods,
    )


@app.route("/edit-page/<int:id>", methods=["GET", "POST"])
@login_required
def edit_page(id):
    page = HistoryPage.query.get(id)

    if request.method == "POST":
        title = request.form.get("title")
        slug = title.lower().replace(" ", "-")
        md_content = request.form.get("content")
        period = request.form.get("period")

        # convert markdown to HTML
        html_content = markdown.markdown(
            md_content, extensions=["tables", "fenced_code"]
        )

        # build the full page
        html_page = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="{{{{ url_for('static', filename='darkstyle.css') }}}}">
            </head>
            <body>
            <h1>{title}</h1>
            <a href="/history" class="back-link">← Back History</a>
            <hr>
            {html_content}
            </body>
            </html>"""

        # delete old file if slug changed
        if slug != page.slug:
            old_filepath = os.path.join(
                "templates", "history_pages", f"{page.slug}.html"
            )
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # save updated file
        filepath = os.path.join("templates", "history_pages", f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_page)

        # update database
        page.title = title
        page.slug = slug
        page.period = period
        page.last_modified = datetime.now(timezone.utc)
        db.session.commit()

        return redirect(f"/pages/{slug}")

    # GET — load existing page content for editing
    filepath = os.path.join("templates", "history_pages", f"{page.slug}.html")
    with open(filepath, "r", encoding="utf-8") as f:
        raw_html = f.read()

    return render_template("edit_page.html", page=page, raw_html=raw_html)


@app.route("/llms")
def llms():
    return render_template("llms_explained.html")


@app.route("/links")
def links():
    category = request.args.get("category", "")
    link_type = request.args.get("type", "")
    page = request.args.get("page", 1, type=int)
    per_page = 20  # <--- number of links displayed per page

    query = Link.query

    if category:
        query = query.filter_by(category=category)
    if link_type:
        query = query.filter_by(type=link_type)

    pagination = query.order_by(Link.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    links = pagination.items

    categories = [r[0] for r in db.session.query(Link.category).distinct().all()]
    types = [r[0] for r in db.session.query(Link.type).distinct().all()]

    return render_template(
        "links.html",
        links=links,
        categories=categories,
        types=types,
        selected_category=category,
        selected_type=link_type,
        pagination=pagination,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == User.username and password == User.password:
            login_user(User())
            next_page = request.args.get("next")
            return redirect(next_page or "/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_link():
    if request.method == "POST":
        url = request.form.get("url")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        new_link = Link(
            url=url,
            title=request.form.get("title"),
            thumbnail=request.form.get("thumbnail"),
            category=request.form.get("category"),
            type=request.form.get("type"),
            date_added=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
        )
        db.session.add(new_link)
        db.session.commit()
        return redirect("/links")

    categories = [r[0] for r in db.session.query(Link.category).distinct().all()]
    types = [r[0] for r in db.session.query(Link.type).distinct().all()]
    return render_template("add_link.html", categories=categories, types=types)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_link(id):
    link = Link.query.get(id)
    if request.method == "POST":
        link.url = request.form.get("url")
        link.title = request.form.get("title")
        link.thumbnail = request.form.get("thumbnail")
        link.category = request.form.get("category")
        link.type = request.form.get("type")
        link.last_modified = datetime.now(timezone.utc)
        db.session.commit()
        return redirect("/links")
    categories = [r[0] for r in db.session.query(Link.category).distinct().all()]
    types = [r[0] for r in db.session.query(Link.type).distinct().all()]
    return render_template(
        "edit_link.html", link=link, categories=categories, types=types
    )


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_link(id):
    link = Link.query.get(id)
    db.session.delete(link)
    db.session.commit()
    return redirect("/links")


@app.route("/fetch-metadata", methods=["POST"])
def fetch_metadata():
    url = request.form.get("url")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        from urllib.parse import urlparse, urljoin

        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title")
        title = title.text.strip() if title else ""

        og_image = soup.find("meta", property="og:image")
        thumbnail = og_image["content"] if og_image else ""

        domain = urlparse(url).netloc
        favicon_google = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"

        favicon_tag = soup.find("link", rel=lambda r: r and "icon" in r)
        favicon_direct = ""
        if favicon_tag and favicon_tag.get("href"):
            href = favicon_tag["href"]
            if href.startswith("http"):
                favicon_direct = href
            elif href.startswith("//"):
                favicon_direct = "https:" + href
            else:
                favicon_direct = urljoin(url, href)

    except:
        title = ""
        thumbnail = ""
        favicon_google = ""
        favicon_direct = ""

    return jsonify(
        {
            "title": title,
            "thumbnail": thumbnail,
            "favicon": favicon_google,
            "favicon_direct": favicon_direct,
            "url": url,
        }
    )


@app.route("/import", methods=["GET", "POST"])
@login_required
def import_page():
    if request.method == "POST":
        title = request.form.get("title")
        slug = title.lower().replace(" ", "-")
        md_content = request.form.get("content")
        period = request.form.get("period")

        # convert markdown to HTML
        html_content = markdown.markdown(
            md_content, extensions=["tables", "fenced_code"]
        )

        # build the full page using your template
        page = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="{{{{ url_for('static', filename='darkstyle.css') }}}}">
            </head>
            <body>
            <h1>{title}</h1>
            <a href="/history" class="back-link">← Back History</a>
            <hr>
            {html_content}
            </body>
            </html>"""

        # save to templates folder
        filepath = os.path.join("templates", "history_pages", f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(page)

        # save to database
        existing = HistoryPage.query.filter_by(slug=slug).first()
        if not existing:
            new_page = HistoryPage(title=title, slug=slug, period=period)
            db.session.add(new_page)
            db.session.commit()

        return redirect(f"/pages/{slug}")

    return render_template("import.html")


@app.route("/pages/<slug>")
def view_page(slug):
    return render_template(f"history_pages/{slug}.html")


download_folder = {"path": os.path.expanduser("~\\Music")}
download_history = []


@app.route("/pick-folder")
@login_required
def pick_folder():
    import tkinter as tk
    from tkinter import filedialog

    folder = {"path": None}

    def open_picker():
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        selected = filedialog.askdirectory()
        if selected:
            folder["path"] = selected
        root.destroy()

    thread = threading.Thread(target=open_picker)
    thread.start()
    thread.join()

    if folder["path"]:
        download_folder["path"] = folder["path"]

    return jsonify({"folder": download_folder["path"]})


@app.route("/converter")
@login_required
def converter():
    return render_template("converter.html", folder=download_folder["path"])


@app.route("/convert", methods=["POST"])
@login_required
def convert():
    url = request.form.get("url")
    folder = download_folder["path"]
    format = request.form.get("format", "mp3")

    if format == "mp4":
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
        }
    else:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Unknown")

    download_history.append(title)
    return jsonify({"status": "ok", "title": title})


@app.route("/download-history")
@login_required
def get_history():
    return jsonify({"history": download_history})


if __name__ == "__main__":
    app.run(debug=True)
