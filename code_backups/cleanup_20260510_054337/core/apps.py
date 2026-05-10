from django.apps import AppConfig


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = _vi(r"Qu\u1ea3n l\u00fd n\u1ed9i dung")
