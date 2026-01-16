from flask import Blueprint, request, session

from models.disabilities import Disablity
from models.profile import Profile
from models.user import User
from models.status import Status
from models.study import Study
from models.enrollment import Enrollment
from view import render, redirect_page
from utils.dropdown import Dropdown
from utils.table import Table
from utils.auth import is_authenticated, in_roles
from werkzeug.exceptions import NotFound, Forbidden
from i18n.locale import get_iso_639_1
from utils.translate import check_translation

users = User()
profiles = Profile()
disabilities = Disablity()
studies = Study()
statuses = Status()
enrollments = Enrollment()

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
    if not is_authenticated():
        return redirect_page("/login")
    user_id = str(session.get("user_id"))
    user = users.get_user_by_id(user_id)
    users.set_user_approve_notifications(user_id)
    profile = profiles.get_profile_by_userid(user_id)
    if profile:
        user_disability_ids = disabilities.get_disability_ids_by_profileid(profile["id"])
        user_disability_ids = tuple(user_disability_ids)
    else:
        user_disability_ids = ()
    profile = profiles.get_profile_by_userid(session["user_id"])
    stats = [0] * 9

    if in_roles("admin"):
        stats[0] = len(users.get_users_by_status(1))
        stats[1] = len(studies.get_study_by_status(1))
        stats[2] = len(enrollments.get_enrollments_by_status(1))

    if in_roles(["expert"]):
        stats[3] = dict(enrollments.count_by_user_id(user_id))["COUNT()"]
        stats[4] = dict(studies.count_available(user_disability_ids))["COUNT(DISTINCT studies.id)"]

    if in_roles(["organization"]):
        stats[6] = len(studies.get_study_by_organization_id(user["organization_id"]))
        stats[7] = (len(studies.get_study_by_status(1)) + len(studies.get_study_by_status(2)) +
                    len(studies.get_study_by_status(2)))
        stats[8] = enrollments.count_by_organization_id(user["organization_id"])

    return render("dashboard.html", profile=profile, stats=stats, user_id=user_id, user=user)


@account_bp.route("/logout")
def account_logout():
    session.clear()
    return render("logout.html")


@account_bp.route("/register", methods=["GET", "POST"])
def account_register():
    page_languages = ['nl', 'en']
    page_translated = check_translation(page_languages, get_iso_639_1())

    success = request.args.get("success")
    error = request.args.get("error")
    errors = {}
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

        # Empty field checks
        required_fields = {
            "email": email,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "gender": gender,
            "disability": disability,
            "postal": postal,
            "intro": intro,
            "phone": phone,
            "birthdate": birthdate,
            "atools": atools,
            "contact": contact,
            "researchtype": researchtype,
            "availability": availability,
            "aterms": aterms,
        }

        for field, value in required_fields.items():
            if not value:
                errors[field] = True

        if not errors:
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
        page_translated=page_translated,
        disabilities=disability_dropdown.export_to_macro(),
        success=success,
        error=error,
        errors=errors,
    )


@account_bp.route("/expert-profile")
def expert_profile_redirect():
    userid = session.get("user_id")
    return redirect_page(f"/expert-profile/{userid}")


@account_bp.route("/expert-profile/<id>")
def expert_profile(id):
    page_languages = ['nl']
    page_translated = check_translation(page_languages, get_iso_639_1())

    userid = session.get("user_id")
    if not is_authenticated() or not in_roles(["admin", "organization", "expert"]):
        raise Forbidden()
    if in_roles("expert") and userid != int(id):
        raise Forbidden()
    allow_delete = False

    if userid == int(id):
        allow_delete = True

    dbuser = users.get_user_by_id(id)
    if not dbuser:
        raise NotFound()
    profile = profiles.get_profile_by_userid(id)
    if not profile:
        raise NotFound()

    disability_list = disabilities.get_disability_list_by_profileid(profile["id"])
    user = {
        **dbuser,
        **profile,
        "disability_list": [disability for disability in disability_list],
    }
    table_header = [
        "category",
        "name",
    ]
    table = Table(user["disability_list"])
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()

    return render(
        "expert-profile.html",
        page_translated=page_translated,
        user=user,
        table_data=table_data,
        allow_delete=allow_delete,
    )


@account_bp.route(
    "/expert-profile/<uid>/delete", methods=["GET", "DELETE", "POST"]
)  # form werkt alleen met post dus standaard geen delete eventueel voor latere api optie
def expert_profile_delete(uid):
    page_languages = ['nl']
    page_translated = check_translation(page_languages, get_iso_639_1())

    userid = session.get("user_id")
    role = session.get("role")
    id = int(uid)

    verified_role = users.get_user_role_by_id(userid)
    if verified_role != role:
        print(f"role forbidden {verified_role} {role}")
        raise Forbidden()

    if int(id) != int(userid):
        print(f"id forbidden {id} {userid} {role}")
        raise Forbidden()

    profile = profiles.get_profile_by_userid(id)
    if not profile:
        raise NotFound()

    if (
        request.method == "POST" or request.method == "DELETE"
    ):  # form werkt alleen met post dus standaard geen delete eventueel voor latere api optie
        users.delete_expert(userid, profiles)  # Need to provide the profiles instance
        session.pop("user_id")
        session.pop("role")
        return redirect_page()

    return render("expert-delete.html", page_translated=page_translated, profile=profile, uid=uid)


@account_bp.route("/expert-profile/<uid>/edit", methods=["GET", "POST"])
# Using Post as this is the only way to avoid using Javascript
def expert_profile_edit(uid):
    page_languages = ['nl']
    page_translated = check_translation(page_languages, get_iso_639_1())

    success = request.args.get("success")
    error = request.args.get("error")
    userid = session.get("user_id")
    role = session.get("role")
    id = int(uid)

    verified_role = users.get_user_role_by_id(userid)
    if verified_role != role:
        print(f"role forbidden {verified_role} {role}")
        raise Forbidden()

    if int(id) != int(userid):
        print(f"id forbidden {id} {userid} {role}")
        raise Forbidden()

    profile = profiles.get_profile_by_userid(id)
    if not profile:
        raise NotFound()

    # Using Post as this is the only way to avoid using Javascript
    if request.method == "POST":
        email = request.form.get("email")
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
            users.update_email(id, email)

            profiles.update_profile(
                userid,
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
            disabilities.update_profile_disabilities(profile["id"], disability)

            return redirect_page(f"/expert-profile/{uid}/edit?success=1")
        except Exception as e:
            message = f"Er is iets fout gegaan"
            print(e)
            return redirect_page(f"/expert-profile/{uid}/edit?error={message}")

    dbuser = users.get_user_by_id(id)
    disability_list = disabilities.get_disability_list_by_profileid(profile["id"])

    user = {
        **dbuser,
        **profile,
        "disability_list": [disability for disability in disability_list],
    }

    disability_dropdown = Dropdown(disabilities.get_all_disabilities())
    disability_dropdown.set("value", "<id>")
    disability_dropdown.set("text", "<name> - <category>")

    return render(
        "expert-profile-edit.html",
        page_translated=page_translated,
        disabilities=disability_dropdown.export_to_macro(),
        user=user,
        success=success,
        error=error,
    )


@account_bp.route("/status")
def account_status():
    page_languages = ['nl']
    page_translated = check_translation(page_languages, get_iso_639_1())

    userid = session.get("user_id")
    user = users.get_user_by_id(userid)
    status = statuses.get_status_name(int(user["status_id"]))
    user["status"] = status
    user["name"] = profiles.get_user_name(userid)

    return render("status-page.html", page_translated=page_translated, user=user)
