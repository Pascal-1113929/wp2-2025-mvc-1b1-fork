import os

from flask import Blueprint

from data.database import Database
from models.enrollment import Enrollment
from models.organization import Organization
from models.study import Study
from models.user import User
from view import render

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)


index_bp = Blueprint('index', __name__)

@index_bp.route("/")
def index(language):
    counts = {
        "experts": users.count_all()[0],
        "organizations": organizations.count_all()[0],
        "studies": studies.count_all()[0],
        "enrollments": enrollments.count_all()[0],
    }

    return render("index.html", counts=counts)
