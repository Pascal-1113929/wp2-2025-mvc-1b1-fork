from datetime import datetime

from flask import Blueprint, request, session

from data.database import DB_PATH
from models.user import User
from models.disabilities import Disablity
from models.profile import Profile
from models.status import Status
from i18n.locale import list_locales
from view import render, redirect_page
from utils.dropdown import Dropdown
from utils.table import Table
from werkzeug.exceptions import NotFound

users = User(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)
statuses = Status(DB_PATH)

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
            user_dict = dict(user)
            if user_dict["status_id"] != 2:
                return redirect_page("/status")
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

            profile_id = profiles.create(
                user_id,
                firstname,
                lastname,
                gender,
                postal,
                intro,
                phone,
                birthdate,
                atools,
                contact,
                researchtype,
                availability,
                aterms,
            )
            disabilities.create_profile_disabilities(profile_id, disability)

            return redirect_page("register?success=1")

        except Exception as e:
            message = f"Er is iets fout gegaan"
            print(e)
            return redirect_page(f"register?error={message}")

    disability_dropdown = Dropdown(disabilities.get_all_disabilities())
    disability_dropdown.set("value", "<id>")
    disability_dropdown.set("text", "<name> - <category>")

    return render(
        "expert-register.html",
        disabilities=disability_dropdown.export_to_macro(),
        success=success,
        error=error,
    )


@account_bp.route("/expert-profile/<id>")
def expert_profile(id):
    userid = session.get("user_id")
    allow_delete = False

    if userid == int(id):
        allow_delete = True

    dbuser = users.get_user_by_id(id)
    profile = profiles.get_profile_by_userid(id)
    if not profile:
        raise NotFound()

    disability_list = disabilities.get_disability_list_by_profileid(profile["id"])
    user = {
        **dbuser,
        **profile,
        "disability_list": [disability for disability in disability_list]
    }
    table_header = [
        "category",
        "name",
    ]
    table = Table(user["disability_list"])
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()
    print(allow_delete)

    return render("expert-profile.html", user=user, table_data=table_data, allow_delete=allow_delete)


@account_bp.route("/expert-delete")
def expert_delete():
    userid = session.get("user_id")
    return render("expert-delete.html")


@account_bp.route("/status")
def account_status():
    userid = session.get("user_id")
    user = users.get_user_by_id(userid)
    status = statuses.get_status_name(int(user["status_id"]))
    user["status"] = status
    user["name"] = profiles.get_user_name(userid)

    return render("status-page.html", user=user)
