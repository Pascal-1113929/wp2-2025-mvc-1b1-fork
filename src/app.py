from flask import Flask

from routes.account import account_bp
from routes.index import index_bp
from routes.organization import org_bp
from routes.research import research_bp
from view import redirect_home, render

app = Flask(__name__)

BLUEPRINTS = {
    "/": index_bp,
    "/organization": org_bp,
    "/account": account_bp,
    "/research": research_bp,
}


@app.route("/")
def goto_locale_page():
    return redirect_home()


@app.errorhandler(404)
def page_not_found(e):
    return render("error/not_found.html"), 404


def remove_language_from_view_args(endpoint, values):
    if values and "language" in values:
        values.pop("language")


for key, value in BLUEPRINTS.items():
    value.url_value_preprocessor(remove_language_from_view_args)
    app.register_blueprint(value, url_prefix="/<language>" + key)


if __name__ == "__main__":
    app.run(debug=True)
