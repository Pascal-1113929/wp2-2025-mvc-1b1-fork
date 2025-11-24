import os

from flask import Flask, redirect, render_template, request

from data.database import Database
from i18n.locale import get_i18n, list_locales
from models.enrollment import Enrollment
from models.organization import Organization
from models.study import Study
from models.user import User

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)


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

@app.errorhandler(404)
def page_not_found(e):
    return render('error/not_found.html'), 404


def render(template, **kwargs):
    language = request.path.split("/")[1]

    if language not in list_locales():
        return redirect_langauge()

    base = {
        "locale": language,
        "language": language.split("-")[0],
        "path": "/" + request.path.split("/", 2)[-1],
    }
    return render_template(template, base=base, lang=get_i18n(language), **kwargs)


def redirect_langauge():
    locale = request.accept_languages.best_match(list_locales())
    return redirect(f"/{locale}", code=302)


if __name__ == "__main__":
    app.run(debug=True)
