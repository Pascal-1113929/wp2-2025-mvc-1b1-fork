from datetime import datetime

from flask import Blueprint, request, session

from data.database import DB_PATH
from models.user import User
from view import render, redirect_page

users = User(DB_PATH)

account_bp = Blueprint("account", __name__)


@account_bp.route("/login", methods=["GET", "POST"])
def account_login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = users.check_login(email, password)
        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect_page("/dashboard")
        else:
            return render("login.html", post_status=1)
    return render("login.html")


@account_bp.route("/dashboard")
def expert_dashboard_render():
    print(session["user_id"], session["role"])
    return render("dashboard.html")
