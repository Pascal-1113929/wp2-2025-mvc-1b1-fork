from datetime import datetime

from flask import Blueprint

from data.database import DB_PATH
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render

users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)

expert_bp = Blueprint("expert", __name__)


@expert_bp.route("/")
def expert_dashboard_render():
    userid = 3  # TODO: get userid from session after login has been completed

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
        study_ids.append(study_id)

    available_studies = []
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

    return render("expert.html", expert=expert, study_list=available_studies)
