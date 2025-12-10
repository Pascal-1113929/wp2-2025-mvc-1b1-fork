from datetime import datetime

from flask import Blueprint, request, session

from data.database import DB_PATH
from models.disabilities import Disablity
from models.profile import Profile
from models.user import User
from view import render, redirect_page

users = User(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)

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

@account_bp.route("/expert-profile/")
def expert_profile():
    userid = 3 #TODO: get id from session after that is implemented (session.get("userid")) and validate role
    dbuser = users.get_user_by_id(userid)
    profile = profiles.get_profile_by_userid(userid)
    disability_list = disabilities.get_disability_list_by_profileid(profile["id"])
    user = {
        **dbuser,
        **profile,
        **disability_list
    }
    print(user)
    return render("expert-profile.html", user=user)
