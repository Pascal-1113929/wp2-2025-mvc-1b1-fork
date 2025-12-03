
from flask import Blueprint

from data.database import DB_PATH
from models.organization import Organization
from models.user import User
from models.study import Study
from view import redirect_home, render
from flask import request, redirect
from i18n.locale import list_locales

organizations = Organization(DB_PATH)
users = User(DB_PATH)
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

@org_bp.route("/register")
def org_register(language):
    success = request.args.get("success")
    error = request.args.get("error")
    return render("organization-register.html", success=success, error=error)
    
@org_bp.route("/register/save", methods=["POST"])
def org_register_save(language):

    email = request.form.get("email")
    password = request.form.get("password")
    
    name = request.form.get("name")
    type = request.form.get("type")
    website = request.form.get("website")
    description = request.form.get("description")
    contact_person = request.form.get("contact_person")
    email = request.form.get("email")
    phone = request.form.get("phone")

    language = request.accept_languages.best_match(list_locales())

    try:
        orgId = organizations.create(
            name, type, website, description, contact_person, email, phone
        )
        
        users.create(
            email, password, organization_id=orgId, role="organization", status="goedgekeurt"
        )
        
        message = "Organisatie succesvol aangemaakt!"
        return redirect(f"/{language}/organization/register?success=1")
    except Exception as e:
        message = f"Er is iets fout gegaan: {str(e)}"
        return redirect(f"/{language}/organization/register?error={message}")
