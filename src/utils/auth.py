from flask import session


def is_authenticated():
    user_id = session.get("user_id")
    if user_id is not None:
        return {"user_id": user_id, "role": session.get("role")}
    return None


def in_roles(role):
    user_role = session.get("role")
    if isinstance(role, list):
        return user_role in role
    return user_role == role
