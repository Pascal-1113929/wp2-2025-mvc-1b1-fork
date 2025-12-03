import os

from flask import Flask

from routes.base import render
from routes.expert import expert_bp
from routes.index import index_bp
from routes.organization import org_bp
from view import redirect_home, render

app = Flask(__name__)
app.register_blueprint(index_bp, url_prefix='/<language>')
app.register_blueprint(org_bp, url_prefix='/<language>/organization')
app.register_blueprint(expert_bp, url_prefix='/<language>/expert')

@app.route("/")
def goto_locale_page():
    return redirect_home()

@app.route("/<language>/debug")
def debug(language):
    return render("debug.html")

@app.route("/<language>/test")
def test(language):
    return render("test.html")

@app.errorhandler(404)
def page_not_found(e):
    return render('error/not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
