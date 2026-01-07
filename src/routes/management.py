from flask import Blueprint

from view import render
from models.user import User
from utils.table import Table

users = User()


management_bp = Blueprint("management", __name__)


@management_bp.route("/")
def index():
    return render("management.html")


@management_bp.route("/approval")
def approval():
    user_table_header = ["email", "notes"]
    print(users.get_new_users())
    user_table = Table(users.get_new_users())

    user_table.whitelist_data(user_table_header)
    user_table.set_order(user_table_header)
    user_table.add_column(
        "options",
        [
            ["button", ["view_profile", ".profile", "fa-solid fa-eye", "info"]],
            [
                "button",
                ["edit_note", ".profile", "fa-solid fa-pen-to-square", "warning"],
            ],
            ["button", ["approve", ".approve", "fa-solid fa-check", ""]],
            ["button", ["reject", ".reject", "fa-solid fa-xmark", "danger"]],
        ],
    )

    user_table_data = user_table.export_to_macro()

    return render("approval.html", user_table=user_table_data)
