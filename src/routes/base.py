from flask import Flask, render_template, redirect, request
from i18n.locale import list_locales, get_i18n
app = Flask(__name__)

def render(template, **kwargs):
    language = request.view_args.get("language")

    if language not in list_locales():
        return redirect_langauge()

    base = {
        "locale": language,
        "language": language.split("-")[0],
        "path": "/" + request.path.split("/", 2)[-1],
    }
    return render_template(template, base=base, lang=get_i18n(language), **kwargs)

def redirect_langauge():
    locale = request.accept_languages.best_match(list_locales())
    return redirect(f"/{locale}", code=302)