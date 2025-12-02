from routes.base import render
from flask import request, redirect
from i18n.locale import list_locales

from models.organization import Organization

def load_web_routes(app):
    @app.route("/<language>/organizations/register", methods=["GET"])
    def org_register(language):
        return render("organization-register.html")
    
    @app.route("/organizations/register/save", methods=["POST"])
    def org_register_save():

        name = request.form.get("name")
        type = request.form.get("type")
        website = request.form.get("website")
        description = request.form.get("description")
        contact_person = request.form.get("contact_person")
        email = request.form.get("email")
        phone = request.form.get("phone")

        language = request.accept_languages.best_match(list_locales())

        try:
            Organization.create(
                name, type, website, description, contact_person, email, phone
            )
            message = "Organisatie succesvol aangemaakt!"
            return redirect(f"/{language}/organizations/register?success=1")
        except Exception as e:
            message = f"Er is iets fout gegaan: {str(e)}"
            return redirect(f"/{language}/organizations/register?error={message}")