from flask import Blueprint, request, render_template, abort

from view import render, redirect_page
from models.user import User
from models.profile import Profile
from models.study import Study
from models.organization import Organization
from models.enrollment import Enrollment
from utils.table import Table
from utils.auth import is_authenticated, in_roles
from utils.mail import send_mail
from i18n.locale import get_i18n
from i18n.locale import get_iso_639_1
from utils.translate import check_translation

users = User()
profile = Profile()
study = Study()
organization = Organization()
enrollment = Enrollment()

approval_bp = Blueprint("approval", __name__)


@management_bp.route("/")
def index():
    if not is_authenticated() or not in_roles("admin"):
        abort(403)
    return render("management.html")


@management_bp.route("/approval")
def approval():
    if not is_authenticated() or not in_roles("admin"):
        abort(403)
    page_languages = ["nl", "en"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    lang = get_i18n()

    user_data = users.get_users_by_status(1)
    research_data = study.get_study_by_status(1)
    for research in research_data:
        org = organization.get_organization_by_id(research["organization_id"])
        research["organization_name"] = org["name"]
    enrollment_data = enrollment.get_enrollments_by_status(1)

    user_table_header = ["email", "notes", "options"]
    research_table_header = ["title", "organization_name", "options"]
    enrollment_table_header = ["expert_name", "study_title", "options"]

    user_table = Table(user_data)
    research_table = Table(research_data)
    enrollment_table = Table(enrollment_data)

    user_table.add_column(
        "options",
        [
            [
                "button",
                [
                    lang.get("approval_users_option_viewprofile"),
                    ".expert-profile/<id>",
                    "fa-solid fa-eye",
                    "info",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_users_option_editnote"),
                    ".approval/note/<id>",
                    "fa-solid fa-pen-to-square",
                    "warning",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_users_option_approve"),
                    ".approval/user/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_users_option_reject"),
                    ".approval/user/<id>/reject",
                    "fa-solid fa-xmark",
                    "danger",
                ],
            ],
        ],
    )

    research_table.add_column(
        "options",
        [
            [
                "button",
                [
                    lang.get("approval_research_option_viewresearch"),
                    ".research/<id>",
                    "fa-solid fa-eye",
                    "info",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_research_option_approve"),
                    ".approval/research/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_research_option_reject"),
                    ".approval/research/<id>/reject",
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
                    lang.get("approval_enrollment_option_viewprofile"),
                    ".expert-profile/<user_id>",
                    "fa-solid fa-eye",
                    "info",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_enrollment_option_viewresearch"),
                    ".research/<study_id>",
                    "fa-solid fa-pen-to-square",
                    "info",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_enrollment_option_approve"),
                    ".approval/enrollment/<id>/approve",
                    "fa-solid fa-check",
                    "",
                ],
            ],
            [
                "button",
                [
                    lang.get("approval_enrollment_option_reject"),
                    ".approval/enrollment/<id>/reject",
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

    ALLOWED_TABS = ["user", "research", "enrollment"]
    tab = request.args.get("tab")

    if tab not in ALLOWED_TABS or tab is None:
        tab = "user"

    alert_id = request.args.get("alert_id")
    alert_field = request.args.get("alert_field")
    alert = None

    def create_alert(type, message):
        if alert_field is not None:
            message = message.replace("%", alert_field)
        return {
            "type": type,
            "message": message,
        }

    match alert_id:
        case "1":
            alert = create_alert("success", lang["approval_alert_" + tab + "_approved"])
        case "2":
            alert = create_alert("success", lang["approval_alert_" + tab + "_rejected"])
        case "3":
            alert = create_alert("success", lang["approval_alert_user_noteedited"])
        case None:
            pass

    return render(
        "approval.html",
        page_translated=page_translated,
        user_table=user_table_data,
        user_table_count=len(user_data),
        research_table=research_table_data,
        research_table_count=len(research_data),
        enrollment_table=enrollment_table_data,
        enrollment_table_count=len(enrollment_data),
        alert_view=alert,
        tab=tab,
    )


def email_generate(
    subject, user_name, user_id, request_type, status, reciever_type="User"
):
    html_email_content = render_template(
        "email/email_template.html",
        subject=subject,
        user_name=user_name,
        request_type=request_type,
        status=status,
    )
    if reciever_type == "User":
        send_mail(subject, html_email_content, users.get_email_by_id(user_id))
    elif reciever_type == "Organization":
        send_mail(subject, html_email_content, organization.get_email_by_id(user_id))
    else:
        raise Exception("Unknown reciever_type")


@approval_bp.route("/<type>/<id>/reject")
def approval_user_reject(type, id):
    if not is_authenticated() or not in_roles("admin"):
        abort(403)
    field_name = ""
    if type == "user":
        field_name = profile.get_name_by_userid(id)
        users.set_user_status(id, 3)
        email_generate(
            "Account Afgekeurd",
            field_name,
            id,
            "Account",
            "Afgekeurd",
        )  # user is default reciever_type
    elif type == "research":
        study.set_research_status(id, 3)
        organization_id = study.get_organization_id_by_id(id)
        field_name = organization.get_name_by_id(organization_id)

        email_generate(
            "Onderzoek Goedgekeurd",
            field_name,
            organization_id,
            "Onderzoek",
            "Goedgekeurd",
            reciever_type="Organization",
        )
    elif type == "enrollment":
        enrollment.set_enrollment_status(id, 3)
        user_id = enrollment.get_user_id_by_enrollment_id(id)
        field_name = profile.get_name_by_userid(user_id)
        email_generate(
            "Inschrijving Afgekeurd",
            field_name,
            user_id,
            "Inschrijving",
            "Afgekeurd",
        )  # user is default reciever_type
    return redirect_page(
        "approval?tab=" + type + "&alert_id=2&alert_field=" + field_name
    )


@approval_bp.route("/<type>/<id>/approve")
def approval_user_approve(type, id):
    if not is_authenticated() or not in_roles("admin"):
        abort(403)
    field_name = ""
    if type == "user":
        field_name = profile.get_name_by_userid(id)

        if not field_name:
            abort(404)

        users.set_user_status(id, 2, 0)
        email_generate(
            "Account Goedgekeurd",
            field_name,
            id,
            "Account",
            "Goedgekeurd",
        )  # user is default reciever_type
    elif type == "research":
        study.set_research_status(id, 2)
        organization_id = study.get_organization_id_by_id(id)
        field_name = organization.get_name_by_id(organization_id)
        email_generate(
            "Onderzoek Goedgekeurd",
            field_name,
            organization_id,
            "Onderzoek",
            "Goedgekeurd",
            reciever_type="Organization",
        )
    elif type == "enrollment":
        enrollment.set_enrollment_status(id, 2)
        user_id = enrollment.get_user_id_by_enrollment_id(id)
        field_name = profile.get_name_by_userid(user_id)
        email_generate(
            "Inschrijving Goedgekeurd",
            field_name,
            user_id,
            "Inschrijving",
            "Goedgekeurd",
        )  # user is default reciever_type
    return redirect_page(
        "approval?tab=" + type + "&alert_id=1&alert_field=" + field_name
    )


@approval_bp.route("/note/<user_id>", methods=["GET", "POST"])
def approval_edit_note(user_id):
    if not is_authenticated() or not in_roles("admin"):
        abort(403)
    user = profile.get_profile_by_userid(user_id)
    field_name = profile.get_name_by_userid(user_id)

    if request.method == "GET":
        if user.get("notes") is None:
            user["notes"] = ""
        return render("approval_edit_note.html", profile_data=user)
    elif request.method == "POST":
        note = request.form.get("note")
        profile.update_note(user_id, note)
        return redirect_page("approval?tab=user&alert_id=3&alert_field=" + field_name)
