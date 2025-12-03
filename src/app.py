
from flask import Flask

from routes.index import index_bp
from view import redirect_home, render

app = Flask(__name__)
app.register_blueprint(index_bp, url_prefix='/<language>')

@app.route("/")
def goto_locale_page():
    return redirect_home()

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

if __name__ == "__main__":
    app.run(debug=True)
