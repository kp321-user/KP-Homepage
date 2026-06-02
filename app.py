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
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import threading
import tkinter as tk
from tkinter import filedialog
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
    return render_template("history.html")


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
            return redirect("/links")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/links")


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
            date_added=datetime.utcnow(),
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
<a href="/" class="back-link">← Back Home</a>
<hr>
{html_content}
</body>
</html>"""

        # save to templates folder
        filepath = os.path.join("templates", f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(page)

        # add route dynamically
        return redirect(f"/pages/{slug}")

    return render_template("import.html")


@app.route("/pages/<slug>")
def view_page(slug):
    return render_template(f"{slug}.html")


download_folder = {"path": os.path.expanduser("~\\Music")}


@app.route("/pick-folder")
@login_required
def pick_folder():
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
        ydl.extract_info(url, download=True)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
