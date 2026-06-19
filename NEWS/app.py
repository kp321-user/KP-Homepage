import os
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
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime, timedelta

load_dotenv()

query = str(input("Enter a search query: "))
from_date = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d")
to_date = datetime.now().strftime("%Y-%m-%d")
sort_by = "relevancy"
client = os.getenv("NEWS_API_KEY")

params = {
    "q": query,
    "sortBy": sort_by,
    "apiKey": client,
}
response = requests.get("https://newsapi.org/v2/everything", params=params)
data = response.json()

if data.get("status") != "ok":
    print("Error:", data.get("message"))
else:
    for article in data["articles"]:
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print("-" * 40)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"BASE_DIR: {BASE_DIR}")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")


@app.route("/articles", methods=["GET", "POST"])
# @login_required
def articles():
    if request.method == "GET":
        new_articles = Article(
            url=request.form.get("url"),
            title=request.form.get("title"),
            thumbnail=request.form.get("thumbnail"),
            category=request.form.get("category"),
            type=request.form.get("type"),
            date_added=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
        )
        return redirect("/articles")


if __name__ == "__main__":
    app.run(debug=True)

# database_url = os.environ.get(
#     "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "kp_db_news1.db")
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = database_url
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)
# csrf = CSRFProtect(app)

# login_manager = LoginManager(app)
# login_manager.login_view = "login"

# ── Single user from environment ──
# class User(UserMixin):
#     id = 1
#     username = os.environ.get("ADMIN_USERNAME", "admin")
#     password = os.environ.get("ADMIN_PASSWORD", "password")


# @login_manager.user_loader
# def load_user(user_id):
#     if int(user_id) == 1:
#         return User()
#     return None


# class Article(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    title = db.Column(db.String(200))
#    url = db.Column(db.String(500))
#    published_at = db.Column(db.DateTime)
#    content = db.Column(db.String(10000))
#    save = db.Column(db.String(200))


# with app.app_context():
#     db.create_all()
