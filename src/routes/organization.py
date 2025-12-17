from flask import Blueprint

from data.database import DB_PATH
from models.organization import Organization
from models.user import User
from models.study import Study
from view import redirect_page, render
from flask import request, redirect
from i18n.locale import list_locales
from utils.table import Table

organizations = Organization(DB_PATH)
users = User(DB_PATH)
studies = Study(DB_PATH)

org_bp = Blueprint("organization", __name__)


@org_bp.route("/")
def organization_list():
    # TODO: list orginisation
    return render("temporary_placeholder.html")


@org_bp.route("/<id>/")
def organization_dashboard_render(id):
    # TODO: validate with a session if the logged in user is a organization and the correct organization
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

        table.set_type("title", "link", [".organization/study/<id>"])
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
        return redirect_page("organization/register?success=1")
    except Exception as e:
        message = f"Er is iets fout gegaan: {str(e)}"
        return redirect_page(f"organization/register?error={message}")
