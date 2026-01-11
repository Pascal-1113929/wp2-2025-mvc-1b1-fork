from flask import request
import os
import yaml

base_directory = os.path.dirname(os.path.abspath(__file__))


def get_i18n(locale=None):
    if locale is None:
        locale = request.path.split("/")[1]

    translation_file = os.path.join(base_directory, "translations", f"{locale}.yaml")
    if not os.path.exists(translation_file):
        translation_file = os.path.join(base_directory, "translations", "nl-NL.yaml")

    with open(translation_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def list_locales():
    locales = []
    for filename in os.listdir(os.path.join(base_directory, "translations")):
        for filetype in ["yaml"]:
            if filename.endswith(filetype):
                locales.append(filename[: -len(filetype) - 1])
    return locales
