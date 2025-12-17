from flask import Blueprint

from data.database import DB_PATH
from models.organization import Organization
from models.user import User
from models.study import Study
from view import redirect_page, render
from flask import request, redirect
from i18n.locale import list_locales
from utils.table import Table
from models.disabilities import Disablity
from models.enrollment import Enrollment
from models.profile import Profile

organizations = Organization(DB_PATH)
users = User(DB_PATH)
studies = Study(DB_PATH)
disabilities = Disablity(DB_PATH)
enrolments = Enrollment(DB_PATH)
profiles = Profile(DB_PATH)

org_bp = Blueprint("organization", __name__)


@org_bp.route("/")
def organization_list():
    # TODO: list orginisation
    return render("temporary_placeholder.html")


@org_bp.route("/<id>/")
def organization_dashboard_render(id):
    user_id = session.get("user_id")
    verified_org_id = users.get_organization_id_by_userid(user_id)['organization_id']
    if verified_org_id != int(id):
        return abort(403)
    org = organizations.get_organization_by_id(id)

    study_table_data = []
    if org is not None:
        study_list = studies.get_study_by_organization_id(id)
        table_header = [
            "title",
            "status",
            "start_date",
            "end_date",
            "study_type",
            "reward",
            "age_min",
            "age_max",
            "modify",
        ]
        table = Table(study_list)

        table.set_type("title", "link", [".organization/<organization_id>/study/<id>"])
        table.add_column(
            "modify", "button", ["delete", ".organization/study/<id>/delete"]
        )
        table.whitelist_data(table_header)
        table.set_order(table_header)

        study_table_data = table.export_to_macro()

    return render("organization.html", organization=org, study_list=study_table_data)


@org_bp.route("/register")
def org_register():
    success = request.args.get("success")
    error = request.args.get("error")
    return render("organization-register.html", success=success, error=error)

@org_bp.route("/register/save", methods=["POST"])
def org_register_save():
    email = request.form.get("email")
    password = request.form.get("password")

    name = request.form.get("name")
    type = request.form.get("type")
    website = request.form.get("website")
    description = request.form.get("description")
    contact_person = request.form.get("contact_person")
    email = request.form.get("email")
    phone = request.form.get("phone")

    try:
        orgId = organizations.create(
            name, type, website, description, contact_person, email, phone
        )

        users.create(
            email,
            password,
            organization_id=orgId,
            role="organization",
            status=2,
        )

        message = "Organisatie succesvol aangemaakt!"
        return redirect_page(f"organization/register?success={message}")
    except Exception as e:
        message = f"Er is iets fout gegaan: {str(e)}"
        return redirect_page(f"organization/register?error={message}")


@org_bp.route("/<oid>/study/<sid>/")
def organization_study_page_render(oid, sid):
    user_id = session.get("user_id")
    verified_org_id = users.get_organization_id_by_userid(user_id)['organization_id']
    if verified_org_id != int(oid):
        print(f"forbidden id mismatch {verified_org_id} {oid}")
        return abort(403)

    org = organizations.get_organization_by_id(oid)
    study = studies.get_study_by_id(sid)
    raw_new_enrolment_list = enrolments.get_enrolments_by_study_id(sid, "nieuw")

    new_enrolment_list = []
    for enrolment in raw_new_enrolment_list:
        profile = profiles.get_profile_by_id(enrolment["profile_id"])
        user = users.get_user_by_id(profile["user_id"])
        new_enrolment = {
            "organization_id": int(oid),
            "study_id": enrolment["study_id"],
            "profile_id": profile["id"],
            "user_id": user["id"],
            "name": profile["first_name"] + " " + profile["last_name"],
            "phonenr": profile["phone"],
            "email": user["email"],
            "contact-preference": profile["contact_preference"],
            "availability": profile["availability"],
        }
        new_enrolment_list.append(new_enrolment)

    table_header = [
        "name",
        "phonenr",
        "email",
        "contact-preference",
        "availability",
        "view_profile",
        "unlist",
    ]
    table = Table(new_enrolment_list)

    table.set_type("title", "link", [".organization/<organization_id>/study/<id>"])
    table.add_column(
        "view_profile", "button", ["Bekijk Profiel", ".expert-profile/<user_id>"]
    )
    table.add_column(
        "unlist", "button", ["Uitschrijven", ".organization/<organization_id>/study/<study_id>/<profile_id>/unlist"]
    )
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()

    if int(oid) != study['organization_id']:
        print("forbidden study_orgid mismatch")
        return abort(403)

    return render("study-org.html", organization=org, study=study, table_data=table_data)

@org_bp.route("<organization_id>/study/<study_id>/<profile_id>/unlist")
def organization_unlist(organization_id, study_id, profile_id):
    organization_id = int(organization_id)
    study_id = int(study_id)
    profile_id = int(profile_id)

    enrolments.delete_enrollment(study_id, profile_id)

    return render("study-org-unlist.html", oid=organization_id, sid=study_id)

@org_bp.route("/research/add", methods=["GET", "POST"])
def research_register():
    if request.method == "GET":
        success = request.args.get("success")
        error = request.args.get("error")
        return render("organization-research.html", success=success, error=error)

    title = request.form.get("title")
    description = request.form.get("description")
    type = request.form.get("type")
    age_min = request.form.get("age_min")
    age_max = request.form.get("age_max")
    reward = request.form.get("reward")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    user = users.get_user_by_id(2)  # TODO: replace with session user id

    try:
        StudyId = studies.create_with_organisation(
            organization_id=user["organization_id"],
            data={
                "title": title,
                "description": description,
                "type": type,
                "min_age": age_min,
                "max_age": age_max,
                "reward": reward,
                "start_date": start_date,
                "end_date": end_date
            }
        )

        message = "Onderzoek succesvol aangemaakt!"
        return redirect_page(f"organization/research/add?success={message}")
    except Exception as e:
        message = f"Er is iets fout gegaan: {str(e)}"
        return redirect_page(f"organization/research/add?error={message}")