import os
from flask import Flask, render_template, redirect, request
from data.database import Database
from models.user import User
from models.organization import Organization
from models.study import Study
from models.enrollment import Enrollment
from i18n.locale import list_locales, get_i18n
from routes.web import load_web_routes
from routes.base import render, redirect_langauge

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)

app.users = users
app.organizations = organizations
app.studies = studies
app.enrollments = enrollments

@app.route("/")
def goto_locale_page():
    return redirect_langauge()


@app.route("/<language>/")
def index(language):
    counts = {
        "experts": users.count_all()[0],
        "organizations": organizations.count_all()[0],
        "studies": studies.count_all()[0],
        "enrollments": enrollments.count_all()[0],
    }

    return render("index.html", counts=counts)


@app.route("/<language>/debug")
def debug(language):
    return render("debug.html")

load_web_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
