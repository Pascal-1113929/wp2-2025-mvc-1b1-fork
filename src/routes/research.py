from datetime import datetime

from flask import Blueprint, session

from data.database import DB_PATH
from models.enrollment import Enrollment
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render, redirect_page
from werkzeug.exceptions import NotFound
from utils.table import Table

users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)
enrolments = Enrollment(DB_PATH)

research_bp = Blueprint("research", __name__)


@research_bp.route("/")
def research_dashboard_render():
    # userid = 3  # TODO: get userid from session after login has been completed
    userid = session.get("user_id")
    # role = session.get("role")

    if userid is None:
        raise NotFound()

    expert_user = dict(users.get_user_by_id(userid))
    expert_profile = dict(profiles.get_profile_by_userid(userid))
    expert_profileid = expert_profile["id"]
    disability_ids = disabilities.get_disability_ids_by_profileid(expert_profileid)

    expert_disabilities = []
    for disability_id in disability_ids:
        disability = disabilities.get_disability_by_id(disability_id)
        expert_disabilities.append(disability)

    expert = {
        "user": expert_user,
        "profile": expert_profile,
        "disabilities": expert_disabilities,
    }

    enrolment_list = enrolments.get_enrolments_by_profile_id(expert_profileid)
    enrolment_study_ids = []
    for enrolment in enrolment_list:
        enrolment_study_ids.append(enrolment["study_id"])

    study_ids = []
    for disability_id in disability_ids:
        study_id_list = studies.get_study_id_by_disability_id(disability_id)
        for study_id in study_id_list:
            study_ids.append(study_id)

    available_studies = []
    for study_id in study_ids:
        if study_id in enrolment_study_ids:
            continue
        study = studies.get_available_study_by_id(study_id)
        if study is None:
            continue
        organization = organizations.get_organization_by_id(study["organization_id"])
        study["organization"] = organization["name"]
        study["location_display"] = study["location"] or study["study_type"]

        # This is needed fo the narrator pronounces the date correctly
        study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
        study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
        study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
        study["end_date"] = study["end_date"].strftime("%d-%m-%Y")
        available_studies.append(study)

    enrolled_studies = []
    for study_id in enrolment_study_ids:
        study = studies.get_available_enrolled_study_by_id(study_id)
        if study is None:
            continue
        organization = organizations.get_organization_by_id(study["organization_id"])
        study["organization"] = organization["name"]
        study["location_display"] = study["location"] or study["study_type"]

        # This is needed fo the narrator pronounces the date correctly
        study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
        study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
        study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
        study["end_date"] = study["end_date"].strftime("%d-%m-%Y")
        enrolled_studies.append(study)

    table_header = [
        "title",
        "organization",
        "start_date",
        "end_date",
        "location_display",
        "reward",
        "age_min",
        "age_max",
    ]

    available_table = Table(available_studies)
    available_table.set_type(
        "title",
        "link",
        [".research/<id>"]
    )
    available_table.whitelist_data(table_header)
    available_table.set_order(table_header)
    available_study_table_data = available_table.export_to_macro()

    enrolled_table = Table(enrolled_studies)
    enrolled_table.set_type(
        "title",
        "link",
        [".research/<id>"]
    )
    enrolled_table.whitelist_data(table_header)
    enrolled_table.set_order(table_header)
    enrolled_study_table_data = enrolled_table.export_to_macro()

    return render("research_list.html",
                  expert=expert,
                  available_study_table_data=available_study_table_data,
                  enrolled_study_table_data=enrolled_study_table_data)


@research_bp.route("/<study_id>")
def study_dashboard_render(study_id):
    user_id = session["user_id"]
    study = studies.get_study_by_id(study_id)
    organization = organizations.get_organization_by_id(study["organization_id"])
    disability_list = disabilities.get_disability_list_by_studyid(study["id"])
    profile = profiles.get_profile_by_userid(user_id)
    enrolled = enrolments.enrolment_check(study["id"], profile["id"])
    study["disabilities"] = disability_list
    table_header = [
        "category",
        "name",
    ]
    table = Table(disability_list)
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()

    return render("study.html", study=study, organization=organization, table_data=table_data, enrolled=enrolled)


@research_bp.route("/<study_id>/enroll")
def enroll_page(study_id):
    user_id = session.get("user_id")

    study = studies.get_study_by_id(study_id)
    user = users.get_user_by_id(user_id)
    profile = profiles.get_profile_by_userid(user_id)

    return render(
        "enroll.html",
        study=study,
        user=user,
        profile=profile
    )


@research_bp.route("/<study_id>/enroll", methods=["POST"])
def enroll_confirm(study_id):
    user_id = session.get("user_id")
    profile = profiles.get_profile_by_userid(user_id)

    enrolments.create(
        profile_id=profile["id"],
        study_id=study_id,
        status=1
    )

    return redirect_page(f"research/{study_id}/enroll/success")


@research_bp.route("/<study_id>/enroll/success")
def enroll_success(study_id):
    return render("enroll_succes.html")


@research_bp.route("/<study_id>/unlist")
def unlist_page(study_id):
    user_id = session.get("user_id")

    study = studies.get_study_by_id(study_id)
    user = users.get_user_by_id(user_id)
    profile = profiles.get_profile_by_userid(user_id)

    return render(
        "unlist.html",
        study=study,
        user=user,
        profile=profile
    )


@research_bp.route("/<study_id>/unlist", methods=["POST"])
def unlist_confirm(study_id):
    user_id = session.get("user_id")
    profile = profiles.get_profile_by_userid(user_id)

    enrolments.delete_enrollment(
        profile_id=profile["id"],
        study_id=study_id,
    )

    return redirect_page(f"research/{study_id}/unlist/success")


@research_bp.route("/<study_id>/unlist/success")
def unlist_success(study_id):
    return render("unlist_success.html")
