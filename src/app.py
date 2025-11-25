from flask import Flask

from routes.index import index_bp
from view import redirect_home, render

app = Flask(__name__)
app.register_blueprint(index_bp, url_prefix='/<language>')


@app.route("/")
def goto_locale_page():
    return redirect_home()

@app.route("/<language>/organization/<id>/")
def organization_dashboard_render(language, id):
    # TODO: validate with a session if the logged in user is a organization and the correct organization
    org = organizations.get_organization_by_id(id)
    if not org:
        # TODO: Display an error
        return redirect("/")

    study_list = studies.get_study_by_organization_id(id)

    return render("organization.html", organization=org, study_list=study_list)


@app.route("/<language>/debug")
def debug(language):
    return render("debug.html")

@app.errorhandler(404)
def page_not_found(e):
    return render('error/not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
