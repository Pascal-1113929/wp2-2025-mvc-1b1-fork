from flask import Blueprint, request, render_template

from view import render, redirect_page
from models.user import User
from models.profile import Profile
from models.study import Study
from models.organization import Organization
from models.enrollment import Enrollment
from utils.table import Table
from utils.mail import send_mail

users = User()
profile = Profile()
study = Study()
organization = Organization()
enrollment = Enrollment()

management_bp = Blueprint("management", __name__)


@management_bp.route("/")
def index():
    return render("management.html")


@management_bp.route("/approval")
def approval():
    user_data = users.get_new_users()
    research_data = study.get_study_by_status(1)
    for research in research_data:
        org = organization.get_organization_by_id(research["organization_id"])
        research["organization_name"] = org["name"]
    enrollment_data = enrollment.get_enrolments_by_status_id(1)

    user_table_header = ["email", "notes", "options"]
    research_table_header = ["title", "organization_name", "options"]
    enrollment_table_header = ["expert_name", "study_title", "options"]

    user_table = Table(user_data)
    research_table = Table(research_data)
    enrollment_table = Table(enrollment_data)

    user_table.add_column(
        "options",
        [
            ["button", ["View profile", ".profile", "fa-solid fa-eye", "info"]],
            [
                "button",
                [
                    "Edit note",
                    ".management/approval/note/<id>",
                    "fa-solid fa-pen-to-square",
                    "warning",
                ],
            ],
            [
                "button",
                [
                    "Approve",
                    ".management/approval/user/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    "Reject",
                    ".management/approval/user/<id>/reject",
                    "fa-solid fa-xmark",
                    "danger",
                ],
            ],
        ],
    )

    research_table.add_column(
        "options",
        [
            ["button", ["View onderzoek", ".research/<id>", "fa-solid fa-eye", "info"]],
            [
                "button",
                [
                    "Approve",
                    ".management/approval/research/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    "Reject",
                    ".management/approval/research/<id>/reject",
                    "fa-solid fa-xmark",
                    "danger",
                ],
            ],
        ],
    )
    enrollment_table.add_column(
        "options",
        [
            [
                "button",
                [
                    "View profile",
                    ".expert-profile/<user_id>",
                    "fa-solid fa-eye",
                    "info",
                ],
            ],
            [
                "button",
                [
                    "View study",
                    ".research/<study_id>",
                    "fa-solid fa-pen-to-square",
                    "info",
                ],
            ],
            [
                "button",
                [
                    "Approve",
                    ".management/approval/enrollment/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    "Reject",
                    ".management/approval/enrollment/<id>/reject",
                    "fa-solid fa-xmark",
                    "danger",
                ],
            ],
        ],
    )

    enrollment_table.add_column(
        "expert_name",
        [
            [
                "text",
                [
                    "<first_name> <last_name>",
                ],
            ]
        ],
    )
    enrollment_table.set_type("study_title", "link", [".research/<study_id>"])

    user_table.whitelist_data(user_table_header)
    research_table.whitelist_data(research_table_header)
    enrollment_table.whitelist_data(enrollment_table_header)

    user_table.set_order(user_table_header)
    research_table.set_order(research_table_header)
    enrollment_table.set_order(enrollment_table_header)

    user_table_data = user_table.export_to_macro()
    research_table_data = research_table.export_to_macro()
    enrollment_table_data = enrollment_table.export_to_macro()

    return render(
        "approval.html",
        user_table=user_table_data,
        user_table_count=len(user_data),
        research_table=research_table_data,
        research_table_count=len(research_data),
        enrollment_table=enrollment_table_data,
        enrollment_table_count=len(enrollment_data),
    )


def email_generate(subject, user_name, user_id, request_type, status, reciever_type="User"):
    html_email_content = render_template(
        "email/email_template.html",
        subject=subject,
        user_name=user_name,
        request_=request_type,
        status=status
    )
    if reciever_type == "User":
        send_mail(subject, html_email_content, users.get_email_by_id(user_id))
    elif reciever_type == "Organization":
        send_mail(subject, html_email_content, organization.get_email_by_id(user_id))
    else:
        raise Exception("Unknown reciever_type")


@management_bp.route("/approval/<type>/<id>/reject")
def approval_user_reject(type, id):
    if type == "user":
        users.set_user_status(id, 3)
        email_generate("Account Afgekeurd",
                       profile.get_name_by_userid(id),
                       id,
                       "Account",
                       "Afgekeurd")  # user is default reciever_type
    elif type == "research":
        study.set_research_status(id, 3)
        organization_id = study.get_organization_id_by_id(id)
        email_generate("Account Goedgekeurd",
                       organization.get_name_by_id(id),
                       organization_id,
                       "Account",
                       "Goedgekeurd",
                       reciever_type="Organization")
    elif type == "enrollment":
        enrollment.set_enrollment_status(id, 3)
        email_generate("Inschrijving Afgekeurd",
                       profile.get_name_by_userid(id),
                       id,
                       "Inschrijving",
                       "Afgekeurd")   # user is default reciever_type
    return redirect_page("management/approval")


@management_bp.route("/approval/<type>/<id>/approve")
def approval_user_approve(type, id):
    if type == "user":
        users.set_user_status(id, 2)
        email_generate("Account Goedgekeurd",
                       profile.get_name_by_userid(id),
                       id,
                       "Account",
                       "Goedgekeurd")  # user is default reciever_type
    elif type == "research":
        study.set_research_status(id, 2)
        organization_id = study.get_organization_id_by_id(id)
        email_generate("Account Goedgekeurd",
                       organization.get_name_by_id(id),
                       organization_id,
                       "Account",
                       "Goedgekeurd",
                       reciever_type="Organization")
    elif type == "enrollment":
        enrollment.set_enrollment_status(id, 2)
        email_generate("Inschrijving Goedgekeurd",
                       profile.get_name_by_userid(id),
                       id,
                       "Inschrijving",
                       "Goedgekeurd")  # user is default reciever_type
    return redirect_page("management/approval")


@management_bp.route("/approval/note/<user_id>", methods=["GET", "POST"])
def approval_edit_note(user_id):
    user = profile.get_profile_by_userid(user_id)
    if request.method == "GET":
        return render("approval_edit_note.html", profile_data=user)
    elif request.method == "POST":
        note = request.form.get("note")
        profile.update_note(user_id, note)
        return redirect_page("management/approval")
