from flask import Flask
from dotenv import load_dotenv
import os

from routes.account import account_bp
from routes.index import index_bp
from routes.organization import org_bp
from routes.research import research_bp
from routes.management import management_bp
from routes.error import error_bp
from view import redirect_page

load_dotenv()

app = Flask(__name__)
app.secret_key = "aseu4a3fh375yaw3kjsddsafa3w95uhdsf"

BLUEPRINTS = {
    "": [error_bp],
    "/": [index_bp, account_bp],
    "/organization": org_bp,
    "/research": research_bp,
    "/management": management_bp,
}


@app.route("/")
def goto_locale_page():
    return redirect_page()


def remove_language_from_view_args(endpoint, values):
    if values and "language" in values:
        values.pop("language")


def register_bp(url_prefix, blueprint):
    blueprint.url_value_preprocessor(remove_language_from_view_args)
    if url_prefix == "":
        app.register_blueprint(blueprint)
    else:
        app.register_blueprint(blueprint, url_prefix="/<language>" + url_prefix)


if __name__ == "__main__":
    # set cache control manually for static files due to twemoji flickering
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600

    for url_prefix, blueprint_or_list in BLUEPRINTS.items():
        if isinstance(blueprint_or_list, list):
            for blueprint in blueprint_or_list:
                register_bp(url_prefix, blueprint)
        else:
            register_bp(url_prefix, blueprint_or_list)
    app.run(debug=True, host=os.getenv("http_host"), port=os.getenv("http_port"))
