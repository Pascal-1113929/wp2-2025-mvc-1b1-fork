from datetime import datetime

from flask import Blueprint, request, redirect
from flask import Blueprint, request, session

from data.database import DB_PATH
from models.user import User
from models.disabilities import Disablity
from models.profile import Profile
from view import render
from i18n.locale import list_locales
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


@account_bp.route("/register", methods=["GET", "POST"])
def account_register():
    success = request.args.get("success")
    error = request.args.get("error")
    if request.method == "POST":
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
        aterms = request.form.get("aterms")

        try:
            user_id = users.create_new_expert(email, password)

            profile_id = profiles.create(user_id, firstname, lastname, gender, postal, intro, phone, birthdate,
                                         atools, contact, researchtype, availability, aterms)
            disabilities.create_profile_disabilities(profile_id, disability)

        except Exception as e:
            message = f"Er is iets fout gegaan"
            return redirect(f"/{language}/account/register?error={message}")

    disability_list = disabilities.get_all_disabilities()
    return render("expert-register.html", disabilities=disability_list, success=success, error=error)