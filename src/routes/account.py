from datetime import datetime

from flask import Blueprint, request, redirect

from data.database import DB_PATH
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render
from i18n.locale import list_locales

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


@account_bp.route("/register")
def account_register():
    success = request.args.get("success")
    error = request.args.get("error")

    disability_list = disabilities.get_all_disabilities()
    return render("expert-register.html", disabilities=disability_list)


@account_bp.route("/register/save")
def account_register_save():
    language = request.accept_languages.best_match(list_locales())

    email = request.form.get("email")
    password = request.form.get("password")

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    gender = request.form.get("gender")
    disability = request.form.get("disability")
    postal = request.form.get("postal")
    intro = request.form.get("intro")
    phone = request.form.get("phone")
    birthdate = request.form.get("birthdate")
    atools = request.form.get("atools")
    contact = request.form.get("contact")
    researchtype = request.form.get("researchtype")
    availability = request.form.get("availability")

    user_id = None
    try:
        user_id = users.create_new_expert(email, password)

    except Exception as e:
        message = f"Er is iets fout gegaan: {str(e)}"
        return redirect(f"/{language}/organization/register?error={message}")

    print(user_id)