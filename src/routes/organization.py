
from flask import Blueprint

from data.database import DB_PATH
from models.organization import Organization
from models.study import Study
from view import redirect_home, render

organizations = Organization(DB_PATH)
studies = Study(DB_PATH)

org_bp = Blueprint('organization', __name__)

@org_bp.route("/<id>/")
def organization_dashboard_render(language, id):
    # TODO: validate with a session if the logged in user is a organization and the correct organization
    org = organizations.get_organization_by_id(id)

    study_list = []
    if org is not None:
        study_list = studies.get_study_by_organization_id(id)

    return render("organization.html", organization=org, study_list=study_list)
