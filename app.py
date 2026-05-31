import os
from flask import Flask, redirect, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///links.db"
db = SQLAlchemy(app)


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
    return render_template("home.html")


@app.route("/python-notes")
def python_notes():
    return render_template("python_notes.html")


@app.route("/links")
def links():
    category = request.args.get("category", "")
    link_type = request.args.get("type", "")

    query = Link.query

    if category:
        query = query.filter_by(category=category)
    if link_type:
        query = query.filter_by(type=link_type)

    links = query.order_by(Link.date_added.desc()).all()

    categories = [r[0] for r in db.session.query(Link.category).distinct().all()]
    types = [r[0] for r in db.session.query(Link.type).distinct().all()]

    return render_template(
        "index.html",
        links=links,
        categories=categories,
        types=types,
        selected_category=category,
        selected_type=link_type,
    )


@app.route("/add", methods=["GET", "POST"])
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

    return render_template("add_link.html")


@app.route("/delete/<int:id>", methods=["POST"])
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
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title")
        title = title.text.strip() if title else ""

        og_image = soup.find("meta", property="og:image")
        thumbnail = og_image["content"] if og_image else ""

    except:
        title = ""
        thumbnail = ""

    return jsonify({"title": title, "thumbnail": thumbnail, "url": url})


if __name__ == "__main__":
    app.run(debug=True)
