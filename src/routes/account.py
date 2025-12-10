from datetime import datetime

from flask import Blueprint

from data.database import DB_PATH
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render

users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)

account_bp = Blueprint("account", __name__)


@account_bp.route("/login")
def account_login():
    return render("login.html")


@account_bp.route("/")
def expert_dashboard_render():
    return render("dashboard.html")

@account_bp.route("/expert-profile/")
def expert_profile():
    userid = 3 #TODO: get id from session after that is implemented (session.get("userid")) and validate role
    dbuser = users.get_user_by_id(userid)
    profile = profiles.get_profile_by_userid(userid)
    user = {
        **dbuser,
        **profile,
    }
    return render("expert-profile.html", user=user)
