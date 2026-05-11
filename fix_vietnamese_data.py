import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import HomeBackground, Lesson
from django.contrib.admin.models import LogEntry


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


BROKEN_TO_FIXED = {
    "?nh n?n trang ch?": _vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7"),
    "?nh n?n": _vi(r"\u1ea2nh n\u1ec1n"),
    "Qu?n trTSA Aptis": _vi(r"Qu\u1ea3n tr\u1ecb TSA Aptis"),
    "Site qu?n trhth?ng": _vi(r"Site qu\u1ea3n tr\u1ecb h\u1ec7 th\u1ed1ng"),
    "Trang ch?": _vi(r"Trang ch\u1ee7"),
    "Ngi Sd?ng": _vi(r"Ng\u01b0\u1eddi s\u1eed d\u1ee5ng"),
    "Ngi Sd?ng": _vi(r"Ng\u01b0\u1eddi s\u1eed d\u1ee5ng"),
    "X?c th?c v?y quy?n": _vi(r"X\u00e1c th\u1ef1c v\u00e0 \u1ee7y quy\u1ec1n"),
    "Ti?u  lesson": _vi(r"Ti\u00eau \u0111\u1ec1 b\u00e0i h\u1ecdc"),
    "Mt?": _vi(r"M\u00f4 t\u1ea3"),
    "N?i dung": _vi(r"N\u1ed9i dung"),
    "Question": _vi(r"C\u00e2u h\u1ecfi"),
    "answer": _vi(r"\u0110\u00e1p \u00e1n"),
}


def fix_text(text):
    if not isinstance(text, str):
        return text

    new = text
    for bad, good in BROKEN_TO_FIXED.items():
        new = new.replace(bad, good)

    return new


for obj in HomeBackground.objects.all():
    new_title = fix_text(obj.title)

    if "?" in new_title or "?" in new_title or new_title.strip() == "":
        new_title = _vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7")

    if new_title != obj.title:
        obj.title = new_title
        obj.save(update_fields=["title"])


for obj in Lesson.objects.all():
    changed = False

    new_title = fix_text(obj.title)
    new_description = fix_text(obj.description)
    new_content = fix_text(obj.content)

    if new_title != obj.title:
        obj.title = new_title
        changed = True

    if new_description != obj.description:
        obj.description = new_description
        changed = True

    if new_content != obj.content:
        obj.content = new_content
        changed = True

    if changed:
        obj.save()


for log in LogEntry.objects.all():
    changed = False

    new_repr = fix_text(log.object_repr)
    new_message = fix_text(log.change_message)

    if "?" in new_repr or "?" in new_repr:
        new_repr = fix_text(new_repr)
        if "?nh" in new_repr or "n?n" in new_repr:
            new_repr = _vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7")

    if new_repr != log.object_repr:
        log.object_repr = new_repr
        changed = True

    if new_message != log.change_message:
        log.change_message = new_message
        changed = True

    if changed:
        log.save(update_fields=["object_repr", "change_message"])


print("DONE:  s?a dli?u ti?ng Vi?t bl?i trong database vadmin log.")
