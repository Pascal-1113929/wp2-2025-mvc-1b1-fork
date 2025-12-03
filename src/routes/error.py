from flask import Blueprint

from view import render

error_bp = Blueprint("error", __name__)


@error_bp.app_errorhandler(404)
def page_not_found(e):
    print("aaaaa")
    return render("error/not_found.html"), 404


@error_bp.app_errorhandler(405)
def method_not_allowed(e):
    return render("error/method_not_allowed.html"), 405


@error_bp.app_errorhandler(500)
def internal_server_error(e):
    return render("error/internal_server_error.html"), 500
