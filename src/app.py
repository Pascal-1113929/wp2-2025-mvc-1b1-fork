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
from routes.expert import expert_bp
from routes.index import index_bp
from routes.organization import org_bp
from view import redirect_home, render

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

app = Flask(__name__)
app.register_blueprint(index_bp, url_prefix='/<language>')
app.register_blueprint(org_bp, url_prefix='/<language>/organization')
app.register_blueprint(expert_bp, url_prefix='/<language>/expert')

@app.route("/")
def goto_locale_page():
    return redirect_home()

@app.route("/<language>/debug")
def debug(language):
    return render("debug.html")

@app.route("/<language>/test")
def test(language):
    return render("test.html")

load_web_routes(app)

@app.errorhandler(404)
def page_not_found(e):
    return render('error/not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
