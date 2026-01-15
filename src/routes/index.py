from flask import Blueprint

from models.enrollment import Enrollment
from models.organization import Organization
from models.study import Study
from models.user import User
from view import render


users = User()
organizations = Organization()
studies = Study()
enrollments = Enrollment()

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    counts = {
        "experts": users.count_all()[0],
        "organizations": organizations.count_all()[0],
        "studies": studies.count_all()[0],
        "enrollments": enrollments.count_all()[0],
    }

    return render("index.html", counts=counts)


@index_bp.route("/debug")
def debug():
    return render("debug.html")
