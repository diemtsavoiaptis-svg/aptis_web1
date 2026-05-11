import os
import sqlite3
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.db import connection, transaction
from core.models import ListeningQuestion

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB = BASE_DIR / "db.sqlite3"
REPORT = BASE_DIR / "SYNC_PART1_AUDIO_TO_ONLINE_FAST_REPORT.txt"

report = []
report.append("SYNC PART 1 AUDIO TO ONLINE FAST REPORT")
report.append(f"Target DB vendor: {connection.vendor}")
report.append(f"Target DB name: {connection.settings_dict.get('NAME')}")

if connection.vendor == "sqlite":
    report.append("STOPPED: Target is SQLite, not Neon/Postgres.")
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    raise SystemExit(1)

conn = sqlite3.connect(str(LOCAL_DB))
conn.row_factory = sqlite3.Row
rows = conn.execute("""
    SELECT
        question_number,
        question_text,
        listening_transcript,
        audio_url,
        voice_info,
        audio_drive_link,
        audio_drive_file_id,
        audio_file_name,
        audio_provider,
        audio_key,
        option_a,
        option_b,
        option_c,
        correct_answer
    FROM core_listeningquestion
    WHERE part = 1
    ORDER BY question_number
""").fetchall()
conn.close()

report.append(f"Local Part 1 rows found: {len(rows)}")

existing = {
    q.question_number: q
    for q in ListeningQuestion.objects.filter(part=1)
}

to_create = []
to_update = []

for row in rows:
    qn = int(row["question_number"])

    obj = existing.get(qn)
    if obj is None:
        obj = ListeningQuestion(
            part=1,
            question_number=qn,
            question_text=row["question_text"] or f"Part 1 - Question {qn}",
            listening_transcript=row["listening_transcript"] or "",
            option_a=row["option_a"] or "A",
            option_b=row["option_b"] or "B",
            option_c=row["option_c"] or "C",
            correct_answer=row["correct_answer"] or "A",
        )
        to_create.append(obj)
    else:
        obj.question_text = row["question_text"] or f"Part 1 - Question {qn}"
        obj.listening_transcript = row["listening_transcript"] or ""
        obj.option_a = row["option_a"] or "A"
        obj.option_b = row["option_b"] or "B"
        obj.option_c = row["option_c"] or "C"
        obj.correct_answer = row["correct_answer"] or "A"

    obj.audio_url = row["audio_url"] or ""
    obj.voice_info = row["voice_info"] or ""
    obj.audio_drive_link = row["audio_drive_link"] or ""
    obj.audio_drive_file_id = row["audio_drive_file_id"] or ""
    obj.audio_file_name = row["audio_file_name"] or ""
    obj.audio_provider = row["audio_provider"] or ""
    obj.audio_key = row["audio_key"] or ""

    if obj.question_number in existing:
        to_update.append(obj)

with transaction.atomic():
    if to_create:
        ListeningQuestion.objects.bulk_create(to_create, batch_size=100)

    if to_update:
        ListeningQuestion.objects.bulk_update(
            to_update,
            [
                "question_text",
                "listening_transcript",
                "audio_url",
                "voice_info",
                "audio_drive_link",
                "audio_drive_file_id",
                "audio_file_name",
                "audio_provider",
                "audio_key",
                "option_a",
                "option_b",
                "option_c",
                "correct_answer",
            ],
            batch_size=100,
        )

qs = ListeningQuestion.objects.filter(part=1)

report.extend([
    f"Created online: {len(to_create)}",
    f"Updated online: {len(to_update)}",
    f"Online Part 1 total: {qs.count()}",
    f"Online with audio_url: {qs.exclude(audio_url='').count()}",
    f"Online with audio_drive_link: {qs.exclude(audio_drive_link='').count()}",
    "",
    "First 20 online rows:",
])

for q in qs.order_by("question_number")[:20]:
    report.append(f"{q.question_number} | {q.audio_file_name} | {q.audio_url[:120]}")

REPORT.write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
