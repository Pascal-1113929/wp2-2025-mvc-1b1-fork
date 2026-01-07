from flask import Blueprint, request

from view import render, redirect_page
from models.user import User
from models.profile import Profile
from utils.table import Table

users = User()
profile = Profile()


management_bp = Blueprint("management", __name__)


@management_bp.route("/")
def index():
    return render("management.html")


@management_bp.route("/approval")
def approval():
    user_table_header = ["email", "notes", "options"]
    user_table = Table(users.get_new_users())

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
            ["button", ["Approve", ".approve", "fa-solid fa-check", ""]],
            ["button", ["Reject", ".reject", "fa-solid fa-xmark", "danger"]],
        ],
    )
    user_table.whitelist_data(user_table_header)
    user_table.set_order(user_table_header)

    user_table_data = user_table.export_to_macro()

    return render("approval.html", user_table=user_table_data)


@management_bp.route("/approval/note/<user_id>", methods=["GET", "POST"])
def approval_edit_note(user_id):
    user = profile.get_profile_by_userid(user_id)
    if request.method == "GET":
        return render("approval_edit_note.html", profile_data=user)
    elif request.method == "POST":
        note = request.form.get("note")
        profile.update_note(user_id, note)
        return redirect_page("management/approval")
