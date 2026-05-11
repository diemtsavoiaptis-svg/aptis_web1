import os
import re
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.db import transaction
from core.models import ListeningQuestion

source = Path("fix_part1_audio_import.py")
text = source.read_text(encoding="utf-8", errors="ignore")

rows = re.findall(
    r"1,(\d+),(.+?\.mp3)\s*(https://drive\.google\.com/file/d/[^\s\"']+)",
    text
)

def extract_drive_id(url):
    m = re.search(r"/file/d/([^/]+)", url)
    return m.group(1) if m else ""

parsed = []
for qn_text, name, link in rows:
    qn = int(qn_text)
    name = name.strip()
    link = link.strip()
    fid = extract_drive_id(link)
    direct = f"https://drive.google.com/uc?export=download&id={fid}" if fid else link
    parsed.append((qn, name, link, fid, direct))

created = 0
updated = 0

with transaction.atomic():
    existing = {
        q.question_number: q
        for q in ListeningQuestion.objects.filter(part=1)
    }

    to_create = []
    to_update = []

    for qn, name, link, fid, direct in parsed:
        obj = existing.get(qn)

        if obj is None:
            obj = ListeningQuestion(
                part=1,
                question_number=qn,
                question_text=f"Part 1 - Question {qn}",
                option_a="A",
                option_b="B",
                option_c="C",
                correct_answer="A",
            )
            created += 1
        else:
            updated += 1

        obj.audio_file_name = name
        obj.audio_drive_link = link
        obj.audio_drive_file_id = fid
        obj.audio_url = direct
        obj.audio_provider = "google_drive"
        obj.audio_key = fid

        if qn in existing:
            to_update.append(obj)
        else:
            to_create.append(obj)

    if to_create:
        ListeningQuestion.objects.bulk_create(to_create, batch_size=100)

    if to_update:
        ListeningQuestion.objects.bulk_update(
            to_update,
            [
                "audio_file_name",
                "audio_drive_link",
                "audio_drive_file_id",
                "audio_url",
                "audio_provider",
                "audio_key",
            ],
            batch_size=100,
        )

qs = ListeningQuestion.objects.filter(part=1)

report = [
    "FIX PART 1 AUDIO IMPORT FAST REPORT",
    f"Rows parsed: {len(rows)}",
    f"Created: {created}",
    f"Updated existing: {updated}",
    f"Part 1 total questions: {qs.count()}",
    f"Part 1 with audio_url: {qs.exclude(audio_url='').count()}",
    f"Part 1 with audio_drive_link: {qs.exclude(audio_drive_link='').count()}",
    "",
    "First 20 rows:",
]

for q in qs.order_by("question_number")[:20]:
    report.append(f"{q.question_number} | {q.audio_file_name} | {q.audio_url}")

Path("FIX_PART1_AUDIO_IMPORT_FAST_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
