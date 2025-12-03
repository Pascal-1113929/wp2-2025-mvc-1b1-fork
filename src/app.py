from datetime import datetime
import os

from flask import Flask, redirect, render_template, request

from data.database import Database
from i18n.locale import get_i18n, list_locales
from models.enrollment import Enrollment
from models.organization import Organization
from models.study import Study
from models.user import User
from models.profile import Profile
from models.disabilities import Disablity

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)
profiles = Profile(DB_PATH)
disabilities = Disablity(DB_PATH)


@app.route("/")
def goto_locale_page():
    return redirect_langauge()


@app.route("/<language>/")
def index(language):
    counts = {
        "experts": users.count_all()[0],
        "organizations": organizations.count_all()[0],
        "studies": studies.count_all()[0],
        "enrollments": enrollments.count_all()[0],
    }

    return render("index.html", counts=counts)


@app.route("/<language>/organization/<id>/")
def organization_dashboard_render(language, id):
    # TODO: validate with a session if the logged in user is a organization and the correct organization
    org = organizations.get_organization_by_id(id)
    if not org:
        # TODO: Display an error
        return redirect("/")

    study_list = studies.get_study_by_organization_id(id)

    return render("organization.html", organization=org, study_list=study_list)


@app.route("/<language>/expert/")
def expert_dashboard_render(language):
    userid = 3  #TODO: get userid from session after login has been completed

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


@app.route("/<language>/debug")
def debug(language):
    return render("debug.html")


@app.errorhandler(404)
def page_not_found(e):
    return render('error/not_found.html'), 404


def render(template, **kwargs):
    language = request.path.split("/")[1]

    if language not in list_locales():
        return redirect_langauge()

    base = {
        "locale": language,
        "language": language.split("-")[0],
        "path": "/" + request.path.split("/", 2)[-1],
    }
    return render_template(template, base=base, lang=get_i18n(language), **kwargs)


def redirect_langauge():
    locale = request.accept_languages.best_match(list_locales())
    return redirect(f"/{locale}", code=302)


if __name__ == "__main__":
    app.run(debug=True)
