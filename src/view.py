from flask import redirect, render_template, request

from i18n.locale import get_i18n, list_locales
from utils.auth import is_authenticated


def render(template, **kwargs):
    language = request.path.split("/")[1]

    if language not in list_locales():
        return redirect_page()

    base = {
        "locale": language,
        "language": language.split("-")[0],
        "path": "/" + request.path.split("/", 2)[-1],
        "user": is_authenticated(),
    }
    return render_template(template, base=base, lang=get_i18n(language), **kwargs)


def redirect_page(path=""):
    locale = request.accept_languages.best_match(list_locales())
    return redirect(f"/{locale}/{path}", code=302)
