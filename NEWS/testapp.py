from flask import Flask, render_template, request

testapp = Flask(__name__)


db = {"title": "Dune", "distributor": "Werner", "runtime": 155}

print(db.get("title"))
print(__name__)

url = "https://search.brave.com/"

@testapp.route("/search", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        title = request.form.get("title")
        url = request.form.get("url")
        return render_template("test.html", title, db)
    else:


@testapp.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        # someone just submitted a form
        title = request.form.get("title")
        ...
    else:
        # someone just visited the page (GET), no form submitted yet
        ...

if __name__ == "__main__":
    testapp.run()
