from datetime import datetime

from flask import Blueprint, session, abort, request

from models.organization import Organization
from models.study import Study
from models.user import User
from models.disabilities import Disablity
from models.enrollment import Enrollment
from models.profile import Profile
from models.status import Status
from utils.table import Table
from utils.dropdown import Dropdown
from utils.auth import is_authenticated, in_roles
from view import redirect_page, render
from utils.translate import check_translation
from i18n.locale import get_iso_639_1
from i18n.locale import get_i18n

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
    page_languages = ['nl', 'en']
    page_translated = check_translation(page_languages, get_iso_639_1())

    if not is_authenticated():
        abort(403)

    if in_roles("admin"):
        lang = get_i18n()
        organization_list = organizations.get_organization_list()
        updated_organization_list = []
        for organization in organization_list:
            organization_id = organization["id"]
            organization_userid_dict = organizations.get_organization_userid(organization_id)
            if organization_userid_dict is None:
                continue
            organization_userid = organization_userid_dict["id"]
            organization["userid"] = organization_userid
            updated_organization_list.append(organization)

        print(updated_organization_list)

        table_header = [
            "name",
            "website",
            "view"
        ]
        organization_table = Table(updated_organization_list)
        organization_table.add_column(
            "view",
            [
                [
                    "button",
                    [
                        lang.get("admin_org_choice_view_btn"),
                        ".organization/<userid>",
                        "fa-solid fa-eye",
                        "info",
                    ],
                ],
            ],
        )
        organization_table.whitelist_data(table_header)
        organization_table.set_order(table_header)
        organization_table_data = organization_table.export_to_macro()

        return render("admin-organization-choice.html",
                      page_translated=page_translated,
                      organization_table_data=organization_table_data,
                      )
    else:
        userid = session.get("user_id")
        return redirect_page(f"/organization/{userid}")


@org_bp.route("/<id>/")
def organization_dashboard_render(id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    if not is_authenticated() or not in_roles(["admin", "organization"]):
        return abort(403)

    close_success = request.args.get("close-success")
    close_error = request.args.get("close-error")
    open_success = request.args.get("open-success")
    open_error = request.args.get("open-error")
    study_id = request.args.get("study_id")
    changes_study = None

    if (
        close_success == "1"
        or close_error == "1"
        or open_success == "1"
        or open_error == "1"
    ):
        if study_id:
            changes_study = studies.get_study_by_id(study_id)

            if changes_study is None:
                changes_study = {
                    "title": "Study Title Not found",
                }

    user_id = session.get("user_id")
    verified_org_id_dict = users.get_organization_id_by_userid(id)

    if not verified_org_id_dict:
        abort(404)

    verified_org_id = verified_org_id_dict["organization_id"]

    if not in_roles("admin"):
        if user_id != int(id):
            return abort(403)
    org = organizations.get_organization_by_id(verified_org_id)

    study_table_data = []
    if org is not None:
        study_list = studies.get_study_by_organization_id(verified_org_id)
        full_study_list = []
        for study in study_list:
            study["location_display"] = study["location"] or study["study_type"]
            full_study_list.append(study)
        table_header = [
            "title",
            "status",
            "start_date",
            "end_date",
            "location_display",
            "reward",
            "age_min",
            "age_max",
            "modify",
        ]
        table = Table(study_list)
        table.set_column_lang("nl", table_header)

        table.set_type("title", "link", [".organization/<organization_id>/study/<id>"])
        table.add_column(
            "modify",
            [
                [
                    "button",
                    [
                        "delete",
                        ".organization/<organization_id>/study/<id>/delete",
                        "fa-solid fa-trash",
                        "danger",
                    ],
                ],
                [
                    "{<status_id> == 2}",
                    "button",
                    [
                        "close",
                        ".organization/<organization_id>/study/<id>/close",
                        "fa-solid fa-trash",
                        "warning",
                    ],
                ],
                [
                    "{<status_id> == 4}",
                    "button",
                    [
                        "re-open",
                        ".organization/<organization_id>/study/<id>/open",
                        "fa-solid fa-trash",
                        "warning",
                    ],
                ],
                [
                    "{<status_id> != 4}",
                    "button",
                    [
                        "edit",
                        ".organization/<organization_id>/study/<id>/edit",
                        "fa-solid fa-trash",
                        "warning",
                    ],
                ],
            ],
        )

        table.whitelist_data(table_header)
        table.set_order(table_header)

        study_table_data = table.export_to_macro()

    return render(
        "organization.html",
        page_translated=page_translated,
        organization=org,
        study_list=study_table_data,
        close_success=close_success,
        close_error=close_error,
        open_success=open_success,
        open_error=open_error,
        study=study,
    )


@org_bp.route("/add", methods=["GET", "POST"])
def org_register_add():
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

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

    return render(
        "organization-add.html",
        page_translated=page_translated,
        success=success,
        error=error,
        errors=errors,
    )


# Dit is na een merge conflict verwijderd en door pascal weer toegevoegd orginele auteur was ALW-2005
# Is aangepast door Pascal na verdere inspectie
@org_bp.route("/research/add", methods=["GET", "POST"])
def research_register():
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

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
        page_translated=page_translated,
        success=success,
        error=error,
        disabilities=disability_dropdown.export_to_macro(),
        errors=errors,
    )


@org_bp.route("/<organization_id>/study/<study_id>/")
def organization_study_page_render(organization_id, study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

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
        page_translated=page_translated,
        organization=org,
        study=study,
        table_data_new=table_data_new,
        table_data_verified=table_data_verified,
    )


@org_bp.route("/<organization_id>/study/<study_id>/close")
def organization_study_close(organization_id, study_id):
    if not is_authenticated():
        return abort(401)

    try:
        studies.set_research_status(study_id, 4)
        return redirect_page(
            f"/organization/{organization_id}?close-success=1&study_id={study_id}"
        )
    except Exception as e:
        print(e)
        return redirect_page(
            f"/organization/{organization_id}?close-error=1&study_id={study_id}"
        )


@org_bp.route("/<organization_id>/study/<study_id>/open")
def organization_study_open(organization_id, study_id):
    if not is_authenticated():
        return abort(401)

    try:
        studies.set_research_status(study_id, 2)
        return redirect_page(
            f"/organization/{organization_id}/?open-success=1&study_id={study_id}"
        )
    except Exception as e:
        print(e)
        return redirect_page(
            f"/organization/{organization_id}/?open-error=1&study_id={study_id}"
        )


@org_bp.route("/<organization_id>/study/<study_id>/edit", methods=["GET", "POST"])
def organization_study_edit_page_render(organization_id, study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    success = request.args.get("success")
    error = request.args.get("error")

    user_id = session.get("user_id")
    verified_org_id = users.get_organization_id_by_userid(user_id)["organization_id"]
    if verified_org_id != int(organization_id):
        print(f"forbidden id mismatch {verified_org_id} {organization_id}")
        return abort(403)

    db_study = studies.get_study_by_id(study_id)
    disability_list = disabilities.get_disability_list_by_studyid(study_id)

    study = {
        **db_study,
        "disability_list": [disability for disability in disability_list],
    }

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
        disability_list = [disability]

        try:
            studies.update_study(
                study_id,
                title,
                description,
                start_date,
                end_date,
                research_type,
                location,
                1 if reward else 0,
                reward,
                age_min,
                age_max,
            )
            disabilities.update_study_disabilities(study_id, disability_list)
            return redirect_page(
                f"/organization/{organization_id}/study/{study_id}/edit?success=1"
            )
        except Exception as e:
            message = f"Er is iets fout gegaan"
            print(e)
            return redirect_page(
                f"/organization/{organization_id}/study/{study_id}/edit?error={message}"
            )

    if success:
        success = "Success Onderzoek gewijzigd!"

    if error:
        error = "Er is iets mis gegaan"

    disability_dropdown = Dropdown(disabilities.get_all_disabilities())
    disability_dropdown.set("value", "<id>")
    disability_dropdown.set("text", "<name> - <category>")

    return render(
        "organization-research-edit.html",
        page_translated=page_translated,
        study=study,
        disabilities=disability_dropdown.export_to_macro(),
        success=success,
        error=error,
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
    page_languages = ["nl", "en"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    organization_id = int(organization_id)
    study_id = int(study_id)
    profile_id = int(profile_id)

    enrolments.delete_enrollment(study_id, profile_id)

    return render(
        "study-org-unlist.html",
        page_translated=page_translated,
        oid=organization_id,
        sid=study_id,
    )
