from datetime import datetime

from flask import Blueprint, session

from data.database import DB_PATH
from models.enrollment import Enrollment
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render
from werkzeug.exceptions import NotFound
from utils.table import Table

users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)

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

    study_ids = []
    for disability_id in disability_ids:
        study_id = studies.get_study_id_by_disability_id(disability_id)
        if study_id is not None:
            study_ids.append(study_id)

    available_studies = []
    print(study_ids)
    for study_id in study_ids:
        study = studies.get_available_study_by_id(study_id)
        organization = organizations.get_organization_by_id(study["organization_id"])
        available_studies.append(study)
        study["organization"] = organization["name"]

        # This is needed fo the narrator pronounces the date correctly
        study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
        study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
        study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
        study["end_date"] = study["end_date"].strftime("%d-%m-%Y")

    return render("research_list.html", expert=expert, study_list=available_studies)


@research_bp.route("/<study_id>")
def study_dashboard_render(study_id):
    study = studies.get_study_by_id(study_id)
    organization = organizations.get_organization_by_id(study["organization_id"])
    disability_list = disabilities.get_disability_list_by_studyid(study["id"])
    study["disabilities"] = disability_list
    table_header = [
        "category",
        "name",
    ]
    table = Table(disability_list)
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()
    print(study)

    return render("study.html", study=study, organization=organization, table_data=table_data)

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
    
    enrollment = Enrollment(DB_PATH)
    enrollment.create(
        user_id=user_id,
        study_id=study_id,
        status = "nieuw"
    )
    
    return render("enroll_success.html")
    

