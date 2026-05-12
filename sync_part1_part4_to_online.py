import os
import json
from pathlib import Path
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import dj_database_url
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent

ONLINE_DATABASE_URL = os.environ.get("ONLINE_DATABASE_URL", "").strip()

if not ONLINE_DATABASE_URL:
    raise SystemExit("ERROR: Missing ONLINE_DATABASE_URL. Please paste your Supabase DATABASE_URL when asked.")

settings.DATABASES["local_sqlite"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}

settings.DATABASES["online"] = dj_database_url.parse(
    ONLINE_DATABASE_URL,
    conn_max_age=600,
    ssl_require=True,
)

import django
django.setup()

from django.core.management import call_command
from django.db import connections, transaction
from django.forms.models import model_to_dict
from core.models import ListeningQuestion, ListeningPartMaterial, ListeningPartQuestion

print("Running online migrations first...")
call_command("migrate", database="online", interactive=False, verbosity=1)

backup_dir = BASE_DIR / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"online_before_sync_part1_part4_{timestamp}.json"

online_part1 = list(ListeningQuestion.objects.using("online").filter(part=1).order_by("id"))
online_part4_materials = list(ListeningPartMaterial.objects.using("online").filter(part=4).order_by("id"))
online_part4_questions = list(
    ListeningPartQuestion.objects.using("online")
    .filter(material__part=4)
    .order_by("id")
)

backup_data = {
    "online_part1": [
        {"id": obj.id, **model_to_dict(obj)}
        for obj in online_part1
    ],
    "online_part4_materials": [
        {"id": obj.id, **model_to_dict(obj)}
        for obj in online_part4_materials
    ],
    "online_part4_questions": [
        {"id": obj.id, **model_to_dict(obj)}
        for obj in online_part4_questions
    ],
}

backup_path.write_text(
    json.dumps(backup_data, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8"
)

print(f"Online backup saved: {backup_path}")

local_part1 = list(ListeningQuestion.objects.using("local_sqlite").filter(part=1).order_by("id"))
local_part4_materials = list(ListeningPartMaterial.objects.using("local_sqlite").filter(part=4).order_by("id"))
local_part4_questions = list(
    ListeningPartQuestion.objects.using("local_sqlite")
    .filter(material__part=4)
    .order_by("id")
)

print()
print("Local data found:")
print(f"- Part 1 questions: {len(local_part1)}")
print(f"- Part 4 materials: {len(local_part4_materials)}")
print(f"- Part 4 questions: {len(local_part4_questions)}")
print()

if not local_part1:
    raise SystemExit("ERROR: No local Part 1 data found in db.sqlite3.")

if not local_part4_materials:
    raise SystemExit("ERROR: No local Part 4 material data found in db.sqlite3.")

with transaction.atomic(using="online"):
    print("Deleting old online Part 1 and Part 4 listening data only...")

    ListeningQuestion.objects.using("online").filter(part=1).delete()
    ListeningPartQuestion.objects.using("online").filter(material__part=4).delete()
    ListeningPartMaterial.objects.using("online").filter(part=4).delete()

    print("Uploading Part 1...")
    for obj in local_part1:
        obj.pk = obj.id
        obj._state.db = "online"
        obj.save(using="online")

    print("Uploading Part 4 materials...")
    for obj in local_part4_materials:
        obj.pk = obj.id
        obj._state.db = "online"
        obj.save(using="online")

    print("Uploading Part 4 questions...")
    for obj in local_part4_questions:
        obj.pk = obj.id
        obj._state.db = "online"
        obj.save(using="online")

def reset_pg_sequence(model):
    table = model._meta.db_table
    pk_col = model._meta.pk.column

    with connections["online"].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence(%s, %s),
                COALESCE((SELECT MAX({pk_col}) FROM {table}), 1),
                (SELECT MAX({pk_col}) FROM {table}) IS NOT NULL
            );
            """,
            [table, pk_col],
        )

reset_pg_sequence(ListeningQuestion)
reset_pg_sequence(ListeningPartMaterial)
reset_pg_sequence(ListeningPartQuestion)

print()
print("DONE: Synced local Part 1 + Part 4 data to online Supabase.")
print(f"Uploaded Part 1 questions: {len(local_part1)}")
print(f"Uploaded Part 4 materials: {len(local_part4_materials)}")
print(f"Uploaded Part 4 questions: {len(local_part4_questions)}")
