from flask import Blueprint, session, abort, request

from models.organization import Organization
from models.study import Study
from models.user import User
from utils.table import Table
from utils.dropdown import Dropdown
from models.disabilities import Disablity
from models.enrollment import Enrollment
from models.profile import Profile
from models.status import Status
from view import redirect_page, render

organizations = Organization()
users = User()
studies = Study()
disabilities = Disablity()
enrolments = Enrollment()
profiles = Profile()
statuses = Status()

org_bp = Blueprint("organization", __name__)


@org_bp.route("/")
def organization_redirect():
    userid = session.get("user_id")
    return redirect_page(f"/organization/{userid}")


@org_bp.route("/<id>/")
def organization_dashboard_render(id):
    user_id = session.get("user_id")
    role = session.get("role")
    verified_org_id = users.get_organization_id_by_userid(user_id)["organization_id"]
    if verified_org_id != int(id) or role == "admin":
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
            "modify",
            [
                [
                    "button",
                    [
                        "delete",
                        ".organization/study/<id>/delete",
                        "fa-solid fa-trash",
                        "danger",
                    ],
                ],
            ],
        )
        table.whitelist_data(table_header)
        table.set_order(table_header)

        study_table_data = table.export_to_macro()

    return render("organization.html", organization=org, study_list=study_table_data)


@org_bp.route("/add", methods=["GET", "POST"])
def org_register_add():
    success = request.args.get("success")
    error = request.args.get("error")
    errors = {}
    if request.method == "POST":
        password = request.form.get("password")
        name = request.form.get("name")
        type = request.form.get("type")
        website = request.form.get("website")
        description = request.form.get("description")
        contact_person = request.form.get("contact_person")
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Check for empty fields
        required_fields = {
            "password": password,
            "name": name,
            "type": type,
            "website": website,
            "description": description,
            "contact_person": contact_person,
            "email": email,
            "phone": phone,
        }

        for field, value in required_fields.items():
            if not value:  # empty string, None, or other falsy values
                errors[field] = True

        if not errors:
            try:
                org_id = organizations.create(
                    name, type, website, description, contact_person, email, phone
                )

                users.create(
                    email,
                    password,
                    organization_id=org_id,
                    role="organization",
                    status=2,
                )

                message = "Organisatie succesvol aangemaakt!"
                return redirect_page("organization/add?success=1")
            except Exception as e:
                message = f"Er is iets fout gegaan: {str(e)}"
                return redirect_page(f"organization/add?error={message}")

    return render("organization-add.html", success=success, error=error, errors=errors)


# Dit is na een merge conflict verwijderd en door pascal weer toegevoegd orginele auteur was ALW-2005
# Is aangepast door Pascal na verdere inspectie
@org_bp.route("/research/add", methods=["GET", "POST"])
def research_register():
    success = request.args.get("success")
    error = request.args.get("error")
    errors = {}
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        research_type = request.form.get("research_type")
        if research_type == "op locatie":
            location = request.form.get("location")
        else:
            location = None
        age_min = request.form.get("age_min")
        age_max = request.form.get("age_max")
        reward = request.form.get("reward")
        disability = request.form.get("disability")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        required_fields = {
            "title": title,
            "description": description,
            "type": research_type,
            "age_min": age_min,
            "age_max": age_max,
            "reward": reward,
            "disability": disability,
            "start_date": start_date,
            "end_date": end_date,
        }

        # Check for empty fields
        for field, value in required_fields.items():
            if not value:
                errors[field] = True

        if research_type == "op locatie":
            if not location:
                errors["location"] = True

        if not errors:
            user = users.get_user_by_id(session.get("user_id"))

            try:
                study_id = studies.create_with_organisation(
                    organization_id=user["organization_id"],
                    data={
                        "title": title,
                        "description": description,
                        "type": research_type,
                        "location": location,
                        "disability": disability,
                        "min_age": age_min,
                        "max_age": age_max,
                        "reward": reward,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                print(study_id)
                disabilities.create_study_disabilities(study_id, disability)

                message = "Onderzoek succesvol aangemaakt!"
                return redirect_page(f"organization/research/add?success={message}")
            except Exception as e:
                message = f"Er is iets fout gegaan: {str(e)}"
                return redirect_page(f"organization/research/add?error={message}")

    disability_dropdown = Dropdown(disabilities.get_all_disabilities())
    disability_dropdown.set("value", "<id>")
    disability_dropdown.set("text", "<name> - <category>")

    return render(
        "organization-research.html",
        success=success,
        error=error,
        disabilities=disability_dropdown.export_to_macro(),
        errors=errors,
    )


@org_bp.route("/<organization_id>/study/<study_id>/")
def organization_study_page_render(organization_id, study_id):
    user_id = session.get("user_id")
    verified_org_id = users.get_organization_id_by_userid(user_id)["organization_id"]
    if verified_org_id != int(organization_id):
        print(f"forbidden id mismatch {verified_org_id} {organization_id}")
        return abort(403)

    org = organizations.get_organization_by_id(organization_id)
    study = studies.get_study_by_id(study_id)
    raw_new_enrolment_list = enrolments.get_enrolments_by_study_id(study_id, 1)
    raw_verified_enrolment_list = enrolments.get_enrolments_by_study_id(study_id, 2)

    new_enrolment_list = []
    for enrolment in raw_new_enrolment_list:
        profile = profiles.get_profile_by_id(enrolment["profile_id"])
        user = users.get_user_by_id(profile["user_id"])
        new_enrolment = {
            "organization_id": int(organization_id),
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

    verified_enrolment_list = []
    for enrolment in raw_verified_enrolment_list:
        profile = profiles.get_profile_by_id(enrolment["profile_id"])
        user = users.get_user_by_id(profile["user_id"])
        verified_enrolment = {
            "organization_id": int(organization_id),
            "study_id": enrolment["study_id"],
            "profile_id": profile["id"],
            "user_id": user["id"],
            "name": profile["first_name"] + " " + profile["last_name"],
            "phonenr": profile["phone"],
            "email": user["email"],
            "contact-preference": profile["contact_preference"],
            "availability": profile["availability"],
        }
        verified_enrolment_list.append(verified_enrolment)

    table_header = [
        "name",
        "phonenr",
        "email",
        "contact-preference",
        "availability",
        "view_profile",
        "unlist",
    ]

    table_data_new = enrolment_table_data_converter(new_enrolment_list, table_header)
    table_data_verified = enrolment_table_data_converter(
        verified_enrolment_list, table_header
    )

    if int(organization_id) != study["organization_id"]:
        print("forbidden study_orgid mismatch")
        return abort(403)

    return render(
        "study-org.html",
        organization=org,
        study=study,
        table_data_new=table_data_new,
        table_data_verified=table_data_verified,
    )


def enrolment_table_data_converter(enrolment_list, table_header):
    table = Table(enrolment_list)

    table.set_type("title", "link", [".organization/<organization_id>/study/<id>"])
    table.add_column(
        "view_profile", "button", ["Bekijk Profiel", ".expert-profile/<user_id>"]
    )
    table.add_column(
        "unlist",
        "button",
        [
            "Uitschrijven",
            ".organization/<organization_id>/study/<study_id>/<profile_id>/unlist",
        ],
    )
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()
    return table_data


@org_bp.route("<organization_id>/study/<study_id>/<profile_id>/unlist")
def organization_unlist(organization_id, study_id, profile_id):
    organization_id = int(organization_id)
    study_id = int(study_id)
    profile_id = int(profile_id)

    enrolments.delete_enrollment(study_id, profile_id)

    return render("study-org-unlist.html", oid=organization_id, sid=study_id)
