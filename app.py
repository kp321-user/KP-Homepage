import os
import markdown
import threading
import uuid
import re
import tempfile
import shutil
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    jsonify,
    abort,
    send_file,
    after_this_request,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
)
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import yt_dlp
from history_periods import HISTORY_PERIODS
from urllib.parse import urlparse

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"BASE_DIR: {BASE_DIR}")  # ------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

database_url = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "kp_db_2026.db")
)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
print(f"DATABASE_URL: {database_url}")  # ------------------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
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
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_modified = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class HistoryPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    is_read = db.Column(db.Integer, default=0)
    era = db.Column(db.String(200))
    period = db.Column(db.String(200))
    phase = db.Column(db.String(200))
    start_year = db.Column(db.Integer)
    content = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_modified = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("home.html", render_env=os.getenv("RENDER"))


@app.route("/python_notes")
def python_notes():
    return render_template("python_notes.html")


@app.route("/github_notes")
def github_notes():
    return render_template("github_notes.html")


@app.route("/beautifulsoup_notes")
def beautifulsoup_notes():
    return render_template("beautifulsoup_notes.html")


@app.route("/streamlit")
def streamlit():
    return render_template("streamlit.html")


@app.route("/venvinfo")
def venvinfo():
    return render_template("windows_paths_venvs_notes.html")


@app.route("/history")
def history():
    sort = request.args.get("sort", "date_added")
    selected_era = request.args.get("era", "")
    selected_period = request.args.get("period", "")
    selected_phase = request.args.get("phase", "")
    selected_is_read = request.args.get("is_read", "")

    query = HistoryPage.query
    if selected_era:
        query = query.filter_by(era=selected_era)
    if selected_period:
        query = query.filter_by(period=selected_period)
    if selected_phase:
        query = query.filter_by(phase=selected_phase)
    if selected_is_read != "":
        query = query.filter_by(is_read=1 if selected_is_read == "true" else 0)
    if sort == "title":
        pages = query.order_by(HistoryPage.title.asc()).all()
    elif sort == "last_modified":
        pages = query.order_by(HistoryPage.last_modified.desc()).all()
    elif sort == "chronological":
        pages = query.order_by(HistoryPage.start_year.asc()).all()
    else:
        pages = query.order_by(HistoryPage.date_added.desc()).all()

    return render_template(
        "history.html",
        render_env=os.getenv("RENDER"),
        history_pages=pages,
        selected_sort=sort,
        selected_era=selected_era,
        selected_period=selected_period,
        selected_phase=selected_phase,
        selected_is_read=selected_is_read,
        periods=HISTORY_PERIODS,
    )


def make_slug(title):
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"_", "-", title)
    title = re.sub(r"\s+", "-", title)
    title = re.sub(r"-+", "-", title)
    return title


@app.route("/toggle-hpage-read/<int:id>", methods=["POST"])
@login_required
def toggle_hpage_read(
    id,
):  # captures the article's id from the URL, e.g. /toggle-hpage-read/42
    page = db.get_or_404(
        HistoryPage, id
    )  # fetches that article from the DB, returns a 404 if it doesn't exist
    page.is_read = 0 if page.is_read else 1
    page.last_modified = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"is_read": page.is_read})


@app.route("/llms")
def llms():
    return render_template("llms_explained.html")


@app.route("/java-notes")
def java_notes():
    return render_template("java_notes.html")


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
            if next_page and urlparse(next_page).netloc:
                next_page = (
                    None  # reject absolute URLs (they have a netloc like "evil.com")
                )
            return redirect(next_page or "/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add-link", methods=["GET", "POST"])
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


@app.route("/edit-link/<int:id>", methods=["GET", "POST"])
@login_required
def edit_link(id):
    link = db.get_or_404(Link, id)
    if request.method == "POST":
        url = request.form.get("url")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        link.url = url
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


@app.route("/delete-link/<int:id>", methods=["POST"])
@login_required
def delete_link(id):
    link = db.get_or_404(Link, id)
    db.session.delete(link)
    db.session.commit()
    return redirect("/links")


@app.route("/fetch-metadata", methods=["POST"])
@csrf.exempt
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

    except Exception as e:
        app.logger.warning(f"fetch_metadata failed: {e}")
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


@app.route("/add-hpage", methods=["GET", "POST"])
@login_required
def add_hpage():
    if request.method == "POST":
        title = request.form.get("title")
        slug = make_slug(title)
        md_content = request.form.get("content")
        era = request.form.get("era")
        period = request.form.get("period")
        phase = request.form.get("phase")
        start_year = request.form.get("start_year")

        existing = HistoryPage.query.filter_by(slug=slug).first()
        if existing:
            existing.title = title
            existing.era = era
            existing.period = period
            existing.phase = phase
            existing.start_year = int(start_year) if start_year else None
            existing.content = md_content
        else:
            new_page = HistoryPage(
                title=title,
                slug=slug,
                era=era,
                period=period,
                phase=phase,
                start_year=int(start_year) if start_year else None,
                content=md_content,
            )
            db.session.add(new_page)

        db.session.commit()

        return redirect(f"/hpages/{slug}")

    return render_template("add_hpage.html", periods=HISTORY_PERIODS)


@app.route("/edit-hpage/<int:id>", methods=["GET", "POST"])
@login_required
def edit_hpage(id):
    page = db.get_or_404(HistoryPage, id)

    if request.method == "POST":
        title = request.form.get("title")
        slug = make_slug(title)

        page.title = title
        page.slug = slug
        page.era = request.form.get("era")
        page.period = request.form.get("period")
        page.phase = request.form.get("phase")
        start_year = request.form.get("start_year")
        page.start_year = int(start_year) if start_year else None
        page.content = request.form.get("content")
        page.last_modified = datetime.now(timezone.utc)
        db.session.commit()

        return redirect(f"/hpages/{slug}")

    return render_template("edit_hpage.html", page=page, periods=HISTORY_PERIODS)


@app.route("/delete-hpage/<int:id>", methods=["POST"])
@login_required
def delete_hpage(id):
    page = db.get_or_404(HistoryPage, id)
    db.session.delete(page)
    db.session.commit()
    return redirect("/history")


@app.route("/hpages/<slug>")
def view_page(slug):
    from jinja2 import TemplateNotFound

    page = HistoryPage.query.filter_by(slug=slug).first()
    if page and page.content is not None:
        html_content = markdown.markdown(
            page.content, extensions=["tables", "fenced_code"]
        )
        return render_template("view_hpage.html", page=page, content=html_content)
    try:
        return render_template(f"history_pages/{slug}.html")
    except TemplateNotFound:
        abort(404)


download_folder = {"path": os.path.expanduser("~\\Music")}
download_history = []
conversion_jobs = (
    {}
)  # job_id -> {status, percent, speed, eta, filepath, filename, error}


def make_progress_hook(job_id):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            percent = round((downloaded / total) * 100, 1) if total else None
            conversion_jobs[job_id].update(
                {
                    "status": "downloading",
                    "percent": percent,
                    "speed": d.get("speed"),
                    "eta": d.get("eta"),
                }
            )
        elif d["status"] == "finished":
            # Download done; if mp3, ffmpeg postprocessing starts next
            conversion_jobs[job_id].update({"status": "processing", "percent": 100})

    return hook


def make_postprocessor_hook(job_id):
    def hook(d):
        # yt-dlp doesn't expose ffmpeg's internal percent here, just phase changes
        if d["status"] == "started":
            conversion_jobs[job_id].update({"status": "processing"})
        elif d["status"] == "finished":
            conversion_jobs[job_id].update({"status": "finalizing"})

    return hook


def run_conversion(job_id, url, frmt):
    tmp_dir = tempfile.mkdtemp()
    cookies_file = None

    try:
        cookies_b64 = os.getenv("YOUTUBE_COOKIES")
        if cookies_b64:
            import base64

            cookies_content = base64.b64decode(cookies_b64).decode("utf-8")
            cf = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
            cf.write(cookies_content)
            cf.close()
            cookies_file = cf.name

        if frmt == "mp4":
            ydl_opts = {
                "format": "best",
                "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
                "noplaylist": True,
                "progress_hooks": [make_progress_hook(job_id)],
            }
        else:
            ydl_opts = {
                "format": "best",
                "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
                "noplaylist": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [make_progress_hook(job_id)],
                "postprocessor_hooks": [make_postprocessor_hook(job_id)],
            }

        if cookies_file:
            ydl_opts["cookiefile"] = cookies_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown")

        files = os.listdir(tmp_dir)
        if not files:
            conversion_jobs[job_id] = {"status": "error", "error": "Download failed"}
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return

        filepath = os.path.join(tmp_dir, files[0])
        download_history.append(title)

        conversion_jobs[job_id].update(
            {
                "status": "done",
                "percent": 100,
                "filepath": filepath,
                "filename": files[0],
                "tmp_dir": tmp_dir,
            }
        )

    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        conversion_jobs[job_id] = {"status": "error", "error": str(e)}

    finally:
        if cookies_file and os.path.exists(cookies_file):
            os.unlink(cookies_file)


@app.route("/csrf-token")
@login_required
def csrf_token():
    return jsonify({"csrf_token": generate_csrf()})


@app.route("/pick-folder")
@login_required
def pick_folder():
    import subprocess, sys

    script = (
        "import tkinter as tk; from tkinter import filedialog; "
        "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
        "path = filedialog.askdirectory(); print(path, end='')"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )
    selected = result.stdout.strip()

    if selected:
        download_folder["path"] = selected

    return jsonify({"folder": download_folder["path"]})


@app.route("/converter")
@login_required
def converter():
    return render_template(
        "converter.html", folder=download_folder["path"], render_env=os.getenv("RENDER")
    )


@app.route("/convert", methods=["POST"])
@login_required
def convert():
    url = request.form.get("url")
    frmt = request.form.get("format", "mp3")

    job_id = str(uuid.uuid4())
    conversion_jobs[job_id] = {"status": "starting", "percent": 0}

    thread = threading.Thread(target=run_conversion, args=(job_id, url, frmt))
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
@login_required
def progress(job_id):
    job = conversion_jobs.get(job_id)
    if not job:
        return jsonify({"status": "unknown"}), 404
    # Don't leak the server filepath to the client
    safe = {k: v for k, v in job.items() if k not in ("filepath", "tmp_dir")}
    return jsonify(safe)


@app.route("/download/<job_id>")
@login_required
def download_result(job_id):
    job = conversion_jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "File not ready"}), 404

    filepath = job["filepath"]
    filename = job["filename"]
    tmp_dir = job["tmp_dir"]

    @after_this_request
    def cleanup(response):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        conversion_jobs.pop(job_id, None)
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route("/download-history")
@login_required
def get_history():
    return jsonify({"history": download_history})


if __name__ == "__main__":
    app.run(debug=True)
