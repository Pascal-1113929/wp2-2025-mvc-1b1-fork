from flask import Blueprint

from view import render


management_bp = Blueprint("management", __name__)


@management_bp.route("/")
def index():
    return render("management.html")
