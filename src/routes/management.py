from flask import Blueprint, request

from view import render, redirect_page
from models.user import User
from models.profile import Profile
from models.study import Study
from utils.table import Table

users = User()
profile = Profile()
study = Study()


management_bp = Blueprint("management", __name__)


@management_bp.route("/")
def index():
    return render("management.html")


@management_bp.route("/approval")
def approval():
    user_data = users.get_new_users()
    research_data = study.get_study_by_status(1)

    user_table_header = ["email", "notes", "options"]
    research_table_header = ["title", "organization_name", "options"]

    user_table = Table(user_data)
    research_table = Table(research_data)

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

    user_table.whitelist_data(user_table_header)
    research_table.whitelist_data(research_table_header)

    user_table.set_order(user_table_header)
    research_table.set_order(research_table_header)

    user_table_data = user_table.export_to_macro()
    return render(
        "approval.html", user_table=user_table_data, user_table_count=len(user_data)
    )


@management_bp.route("/approval/user/<user_id>/reject")
def approval_user_reject(user_id):
    users.set_user_status(user_id, 3)
    return redirect_page("management/approval")


@management_bp.route("/approval/user/<user_id>/approve")
def approval_user_approve(user_id):
    users.set_user_status(user_id, 2)
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
