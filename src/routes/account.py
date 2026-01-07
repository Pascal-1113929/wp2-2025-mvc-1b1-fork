from flask import Blueprint, request, session

from data.database import DB_PATH
from models.disabilities import Disablity
from models.profile import Profile
from models.user import User
from utils.authorization import is_authenticated
from utils.dropdown import Dropdown
from view import redirect_page, render

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
    if not is_authenticated():
        return redirect_page("/login")
    return render("dashboard.html")


@account_bp.route("/logout")
def account_logout():
    session.clear()
    return render("logout.html")


@account_bp.route("/register", methods=["GET", "POST"])
def account_register():
    success = request.args.get("success")
    error = request.args.get("error")
    if request.method == "POST":
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
            message = "Er is iets fout gegaan"
            print(e)
            return redirect_page(f"register?error={message}")

    disability_dropdown = Dropdown(disabilities.get_all_disabilities())
    disability_dropdown.set("value", "<id>")
    disability_dropdown.set("text", "<name> - <category>")

    return render(
        "register.html",
        disabilities=disability_dropdown.export_to_macro(),
        success=success,
        error=error,
    )
