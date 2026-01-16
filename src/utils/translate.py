def check_translation(available_languages: list, target_language: str):
    if target_language not in available_languages:
        return False
    else:
        return True
