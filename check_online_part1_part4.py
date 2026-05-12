import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import dj_database_url
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent
ONLINE_DATABASE_URL = os.environ.get("ONLINE_DATABASE_URL", "").strip()

settings.DATABASES["online"] = dj_database_url.parse(
    ONLINE_DATABASE_URL,
    conn_max_age=600,
    ssl_require=True,
)

import django
django.setup()

from core.models import ListeningQuestion, ListeningPartMaterial, ListeningPartQuestion

print("===== ONLINE DATA CHECK =====")
print()

part1_total = ListeningQuestion.objects.using("online").filter(part=1).count()
part1_audio = ListeningQuestion.objects.using("online").filter(part=1).exclude(audio_url="").count()
part1_drive = ListeningQuestion.objects.using("online").filter(part=1).exclude(audio_drive_link="").count()

part4_total = ListeningPartMaterial.objects.using("online").filter(part=4).count()
part4_audio = ListeningPartMaterial.objects.using("online").filter(part=4).exclude(audio_url="").count()
part4_questions = ListeningPartQuestion.objects.using("online").filter(material__part=4).count()

print(f"Part 1 total questions: {part1_total}")
print(f"Part 1 rows with audio_url: {part1_audio}")
print(f"Part 1 rows with audio_drive_link: {part1_drive}")
print()
print(f"Part 4 total materials: {part4_total}")
print(f"Part 4 materials with audio_url: {part4_audio}")
print(f"Part 4 total questions: {part4_questions}")
print()

print("===== PART 4 AUDIO CHECK 1-54 =====")
materials = list(
    ListeningPartMaterial.objects.using("online")
    .filter(part=4)
    .order_by("id")
)

missing = []

for i, m in enumerate(materials[:54], start=1):
    status = "OK" if m.audio_url else "MISSING"
    print(f"{i}. ID={m.id} | {status} | {m.title} | {m.audio_url}")
    if not m.audio_url:
        missing.append(i)

print()
if missing:
    print("MISSING AUDIO ROWS:", missing)
else:
    print("All Part 4 rows 1-54 have audio_url.")

print()
print("===== QUICK RESULT =====")
if part1_total == 191 and part4_audio >= 54:
    print("OK: Online database has Part 1 data and Part 4 audio 1-54.")
else:
    print("WARNING: Online data is not complete yet.")
