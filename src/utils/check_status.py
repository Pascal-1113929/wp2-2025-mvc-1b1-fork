from models.user import User

from flask import session

from view import redirect_page

users = User()

def check_status(user_id):
    user_id = str(session.get("user_id"))
    user = users.get_user_by_id(user_id)
    if user["status_id"] != 2:
        return redirect_page("/status")