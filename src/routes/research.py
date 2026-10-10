from datetime import datetime, date
from functools import wraps
from math import ceil
from urllib.parse import urlencode

from flask import Blueprint, session, render_template, request, url_for

from models.enrollment import Enrollment
from models.disabilities import Disablity
from models.organization import Organization
from models.profile import Profile
from models.study import Study
from models.user import User
from view import render, redirect_page
from werkzeug.exceptions import NotFound, abort
from utils.table import Table
from utils.auth import in_roles, is_authenticated
from utils.mail import send_mail
from i18n.locale import get_iso_639_1
from utils.translate import check_translation

users = User()
organizations = Organization()
studies = Study()
profiles = Profile()
disabilities = Disablity()
enrolments = Enrollment()

research_bp = Blueprint("research", __name__)

def require_active_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("text")
        user_id = session.get("user_id")
        if user_id is None:
            raise NotFound()
        user = users.get_user_by_id(str(user_id))
        if user["status_id"] != 2:
            return redirect_page("/status")
        return func(*args, **kwargs)
    return wrapper


@research_bp.route("/")
@require_active_status
def research_dashboard_render():
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())
    search_query = request.args.get("search", "").lower()
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)
    study_type = request.args.getlist("study_type", type=str)
    selected_columns = request.args.getlist("selected_columns", type=str)

    userid = session.get("user_id")
    role = session.get("role")
    is_expert = False

    if userid is None:
        raise NotFound()

    tab = request.args.get("tab")

    args = request.args.to_dict(flat=True)
    args.pop("tab", None)  # Remove 'tab' key if present
    extra_args = "&" + urlencode(args)

    # Available studies
    available_page = request.args.get("available_page", 1, type=int)
    if available_page < 1:
        available_page = 1

    # Enrolled studies
    enrolled_page = request.args.get("enrolled_page", 1, type=int)
    if enrolled_page < 1:
        enrolled_page = 1

    preferences_values = request.args.getlist("preferences")
    if preferences_values:
        show_matching = 1 if "1" in preferences_values else 0
    else:
        show_matching = 1

    if role == "expert":

        is_expert = True
        expert_user = dict(users.get_user_by_id(userid))
        expert_profile = dict(profiles.get_profile_by_userid(userid))
        expert_profileid = expert_profile["id"]
        disability_ids = disabilities.get_disability_ids_by_profileid(expert_profileid)

        expert_disabilities = []
        for disability_id in disability_ids:
            disability = disabilities.get_disability_by_id(disability_id)
            expert_disabilities.append(disability)

        expert = {
            "user": expert_user,
            "profile": expert_profile,
            "disabilities": expert_disabilities,
        }

        enrolment_list = enrolments.get_enrolments_by_profile_id(expert_profileid)
        enrolment_study_ids = []
        for enrolment in enrolment_list:
            enrolment_study_ids.append(enrolment["study_id"])

        study_ids = []
        if not show_matching:
            study_ids = studies.get_all_available_ids()
        else:
            for disability_id in disability_ids:
                study_id_list = studies.get_study_id_by_disability_id(disability_id)
                for study_id in study_id_list:
                    study_ids.append(study_id)

        available_studies = []
        for study_id in study_ids:
            if study_id in enrolment_study_ids:
                continue
            study = studies.get_available_study_by_id(study_id)
            profile_birth_date = datetime.strptime(
                expert["profile"]["birth_date"], "%Y-%m-%d"
            ).date()

            today = date.today()
            age = (
                today.year
                - profile_birth_date.year
                - (
                    (today.month, today.day)
                    < (profile_birth_date.month, profile_birth_date.day)
                )
            )

            if study is None:
                continue

            if show_matching:
                if expert["profile"]["preferred_study_type"] != study["study_type"]:
                    continue
                if not (study["age_min"] <= age <= study["age_max"]):
                    continue

            organization = organizations.get_organization_by_id(
                study["organization_id"]
            )
            study["organization"] = organization["name"]
            study["location_display"] = study["location"] or study["study_type"]

            # This is needed fo the narrator pronounces the date correctly
            study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
            study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
            study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
            study["end_date"] = study["end_date"].strftime("%d-%m-%Y")
            available_studies.append(study)

        if search_query:
            available_studies = [
                study
                for study in available_studies
                if search_query in study["title"].lower()
                or search_query in study["organization"].lower()
                or search_query in study["location_display"].lower()
            ]
        if age_min is not None:
            available_studies = [
                study for study in available_studies if study["age_min"] >= age_min
            ]
        if age_max is not None:
            available_studies = [
                study for study in available_studies if study["age_max"] <= age_max
            ]
        if study_type:
            available_studies = [
                study
                for study in available_studies
                if study["study_type"] in study_type
            ]

        enrolled_studies = []
        for study_id in enrolment_study_ids:
            study = studies.get_available_enrolled_study_by_id(study_id)
            if study is None:
                continue

            if tab and tab != "None":
                if study["astatus_id"] != int(tab):
                    continue
            organization = organizations.get_organization_by_id(
                study["organization_id"]
            )
            study["organization"] = organization["name"]
            study["location_display"] = study["location"] or study["study_type"]

            # This is needed fo the narrator pronounces the date correctly
            study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
            study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
            study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
            study["end_date"] = study["end_date"].strftime("%d-%m-%Y")
            enrolled_studies.append(study)

    if role == "admin" or role == "organization":
        study_list = studies.get_all_available()
        available_studies = []
        for study in study_list:
            if study is None:
                continue
            organization = organizations.get_organization_by_id(
                study["organization_id"]
            )
            study["organization"] = organization["name"]
            study["location_display"] = study["location"] or study["study_type"]

            # This is needed fo the narrator pronounces the date correctly
            study["start_date"] = datetime.strptime(study["start_date"], "%Y-%m-%d")
            study["end_date"] = datetime.strptime(study["end_date"], "%Y-%m-%d")
            study["start_date"] = study["start_date"].strftime("%d-%m-%Y")
            study["end_date"] = study["end_date"].strftime("%d-%m-%Y")
            available_studies.append(study)

        if search_query:
            available_studies = [
                study
                for study in available_studies
                if search_query in study["title"].lower()
                or search_query in study["organization"].lower()
                or search_query in study["location_display"].lower()
            ]
        if age_min is not None:
            available_studies = [
                study for study in available_studies if study["age_min"] >= age_min
            ]
        if age_max is not None:
            available_studies = [
                study for study in available_studies if study["age_max"] <= age_max
            ]
        if study_type:
            available_studies = [
                study
                for study in available_studies
                if study["study_type"] in study_type
            ]

        enrolled_studies = []
        expert = None

    # Available studies page size
    available_page_size = request.args.get("available_page_size", 10, type=str)
    if available_page_size == "":
        available_page_size = 10

    # Enrolled studies page size
    enrolled_page_size = request.args.get("enrolled_page_size", 10, type=str)
    if enrolled_page_size == "":
        enrolled_page_size = 10

    # Available studies page size
    if available_page_size == "all":
        available_PAGE_SIZE = len(available_studies)
    else:
        try:
            available_PAGE_SIZE = int(available_page_size)
        except ValueError:
            available_PAGE_SIZE = 10

    # Enrolled studies page size
    if enrolled_page_size == "all":
        enrolled_PAGE_SIZE = len(enrolled_studies)
    else:
        try:
            enrolled_PAGE_SIZE = int(enrolled_page_size)
        except ValueError:
            available_PAGE_SIZE = 10

    # Available studies pagination
    total_available = len(available_studies)
    if available_PAGE_SIZE != 0:
        total_pages_available = ceil(total_available / available_PAGE_SIZE)
    else:
        total_pages_available = 0
    start = (available_page - 1) * available_PAGE_SIZE
    end = start + available_PAGE_SIZE
    available_studies_paginated = available_studies[start:end]

    # Enrolled studies pagination
    total_enrolled = len(enrolled_studies)
    if enrolled_PAGE_SIZE != 0:
        total_pages_enrolled = ceil(total_enrolled / enrolled_PAGE_SIZE)
    else:
        total_pages_available = 0
    start = (enrolled_page - 1) * enrolled_PAGE_SIZE
    end = start + enrolled_PAGE_SIZE
    enrolled_studies_paginated = enrolled_studies[start:end]

    if not selected_columns:
        selected_columns = [
            "title",
            "organization",
            "start_date",
            "end_date",
            "location_display",
            "reward",
            "age_min",
            "age_max",
        ]

    if "title" not in selected_columns:
        selected_columns.insert(0, "title")  # insert at the beginning

    table_header = selected_columns

    available_table = Table(available_studies_paginated)
    available_table.set_type("title", "link", [".research/<id>"])
    available_table.whitelist_data(table_header)
    available_table.set_order(table_header)
    available_study_table_data = available_table.export_to_macro()

    enrolled_table = Table(enrolled_studies_paginated)
    enrolled_table.set_type("title", "link", [".research/<id>"])
    enrolled_table.whitelist_data(table_header)
    enrolled_table.set_order(table_header)
    enrolled_study_table_data = enrolled_table.export_to_macro()

    return render(
        "research_list.html",
        page_translated=page_translated,
        expert=expert,
        is_expert=is_expert,
        available_study_table_data=available_study_table_data,
        enrolled_study_table_data=enrolled_study_table_data,
        # pagination metadata
        available_page=available_page,
        total_pages_available=total_pages_available,
        has_prev_available=available_page > 1,
        has_next_available=available_page < total_pages_available,
        available_page_size=str(available_page_size),
        enrolled_page=enrolled_page,
        total_pages_enrolled=total_pages_enrolled,
        has_prev_enrolled=enrolled_page > 1,
        has_next_enrolled=enrolled_page < total_pages_enrolled,
        enrolled_page_size=str(enrolled_page_size),
        tab=tab,
        extra_args=extra_args,
        selected_columns=selected_columns,
        show_matching=show_matching,
    )


@research_bp.route("/<study_id>")
@require_active_status
def study_dashboard_render(study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    if in_roles("expert"):
        user_id = session["user_id"]

    study = studies.get_study_by_id(study_id)
    if study is None:
        abort(404)

    organization = organizations.get_organization_by_id(study["organization_id"])
    disability_list = disabilities.get_disability_list_by_studyid(study["id"])
    if in_roles("expert"):
        profile = profiles.get_profile_by_userid(user_id)
        enrolled = enrolments.enrolment_check(study["id"], profile["id"])
    study["disabilities"] = disability_list
    table_header = [
        "category",
        "name",
    ]
    table = Table(disability_list)
    table.whitelist_data(table_header)
    table.set_order(table_header)

    table_data = table.export_to_macro()

    return render(
        "study.html",
        page_translated=page_translated,
        study=study,
        organization=organization,
        table_data=table_data,
        enrolled=enrolled if in_roles("expert") else None,
    )


@research_bp.route("/<study_id>/enroll")
@require_active_status
def enroll_page(study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    if not is_authenticated() or not in_roles("expert"):
        abort(403)

    user_id = session.get("user_id")

    study = studies.get_study_by_id(study_id)
    user = users.get_user_by_id(user_id)
    profile = profiles.get_profile_by_userid(user_id)

    return render(
        "enroll.html",
        page_translated=page_translated,
        study=study,
        user=user,
        profile=profile,
    )


@research_bp.route("/<study_id>/enroll", methods=["POST"])
@require_active_status
def enroll_confirm(study_id):
    if not is_authenticated() or not in_roles("expert"):
        abort(403)

    user_id = session.get("user_id")
    profile = profiles.get_profile_by_userid(user_id)
    user_name = profiles.get_name_by_userid(user_id)
    study_name = studies.get_study_by_id(study_id)["title"]

    enrolments.create(profile_id=profile["id"], study_id=study_id, status=1)

    subject = f"Inschrijving Onderzoek: {study_name}"
    html_email_content = render_template(
        "email/email_enroll_template.html",
        subject=subject,
        user_name=user_name,
        study_name=study_name,
    )
    send_mail(subject, html_email_content, users.get_email_by_id(user_id))

    return redirect_page(f"research/{study_id}/enroll/success")


@research_bp.route("/<study_id>/enroll/success")
def enroll_success(study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    return render("enroll_succes.html", page_translated=page_translated)


@research_bp.route("/<study_id>/unlist")
@require_active_status
def unlist_page(study_id):
    page_languages = ["nl"]

    if not is_authenticated() or not in_roles("expert"):
        abort(403)

    user_id = session.get("user_id")

    study = studies.get_study_by_id(study_id)
    user = users.get_user_by_id(user_id)
    profile = profiles.get_profile_by_userid(user_id)

    return render("unlist.html", study=study, user=user, profile=profile)


@research_bp.route("/<study_id>/unlist", methods=["POST"])
def unlist_confirm(study_id):
    if not is_authenticated() or not in_roles("expert"):
        abort(403)

    user_id = session.get("user_id")
    profile = profiles.get_profile_by_userid(user_id)

    enrolments.delete_enrollment(
        profile_id=profile["id"],
        study_id=study_id,
    )

    return redirect_page(f"research/{study_id}/unlist/success")


@research_bp.route("/<study_id>/unlist/success")
def unlist_success(study_id):
    page_languages = ["nl"]
    page_translated = check_translation(page_languages, get_iso_639_1())

    return render("unlist_success.html", page_translated=page_translated)
