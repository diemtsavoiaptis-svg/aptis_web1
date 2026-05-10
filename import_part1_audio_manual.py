import os
import re
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import ListeningQuestion


def extract_drive_file_id(value):
    value = str(value or "").strip()
    patterns = [
        r"/file/d/([^/]+)",
        r"id=([^&]+)",
        r"/d/([^/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1).strip()

    return ""


print("=" * 70)
print("PASTE BANG AUDIO PART 1 VAO DAY")
print("DAN XONG, GO RIENG 1 DONG: END_AUDIO")
print("=" * 70)

lines = []

while True:
    line = sys.stdin.readline()

    if not line:
        break

    if line.strip() == "END_AUDIO":
        break

    lines.append(line)

raw_text = "".join(lines).strip()

if not raw_text:
    raise SystemExit("CHUA CO DU LIEU AUDIO. Hay chay lai va dan bang audio vao.")

Path("part1_audio_drive.txt").write_text(raw_text, encoding="utf-8")

rows = []

for raw_line in raw_text.splitlines():
    line = raw_line.strip()

    if not line:
        continue

    if line.lower().startswith("part") or line.lower().startswith("question"):
        continue

    match = re.search(r"(https://drive\.google\.com/\S+)", line)

    if not match:
        continue

    drive_link = match.group(1).strip()
    left = line[:match.start()].strip(" ,\t")

    if "," in left:
        parts = left.split(",", 2)
    else:
        parts = re.split(r"\t+", left, maxsplit=2)

    if len(parts) < 3:
        print("Skip line:", line[:120])
        continue

    try:
        part = int(parts[0].strip())
        question_number = int(parts[1].strip())
    except ValueError:
        print("Skip wrong number:", line[:120])
        continue

    audio_file_name = parts[2].strip()
    drive_file_id = extract_drive_file_id(drive_link)

    if not drive_file_id:
        raise SystemExit(f"Cannot extract Drive ID at question {question_number}: {drive_link}")

    rows.append({
        "part": part,
        "question_number": question_number,
        "audio_file_name": audio_file_name,
        "audio_drive_link": drive_link,
        "audio_drive_file_id": drive_file_id,
    })


if not rows:
    raise SystemExit("KHONG DOC DUOC DONG AUDIO NAO.")

rows.sort(key=lambda item: item["question_number"])

numbers = [item["question_number"] for item in rows]
missing = [n for n in range(1, 192) if n not in numbers]
duplicates = sorted({n for n in numbers if numbers.count(n) > 1})

print("=" * 70)
print("CHECK AUDIO PART 1")
print("=" * 70)
print("Total rows:", len(rows))
print("First question:", numbers[0])
print("Last question:", numbers[-1])

if duplicates:
    raise SystemExit(f"Duplicate questions: {duplicates}")

if missing:
    raise SystemExit(f"Missing questions: {missing}")

if len(rows) != 191:
    raise SystemExit(f"Need 191 rows, got {len(rows)} rows.")

created = 0
updated = 0

for item in rows:
    obj, was_created = ListeningQuestion.objects.get_or_create(
        part=item["part"],
        question_number=item["question_number"],
        defaults={
            "question_text": f"Câu hỏi Listening Part {item['part']} - Câu {item['question_number']}",
            "option_a": "Đáp án A",
            "option_b": "Đáp án B",
            "option_c": "Đáp án C",
            "correct_answer": "A",
        }
    )

    obj.audio_drive_link = item["audio_drive_link"]
    obj.audio_drive_file_id = item["audio_drive_file_id"]

    if hasattr(obj, "audio_file_name"):
        obj.audio_file_name = item["audio_file_name"]

    if not obj.question_text:
        obj.question_text = f"Câu hỏi Listening Part {item['part']} - Câu {item['question_number']}"

    if not obj.option_a:
        obj.option_a = "Đáp án A"

    if not obj.option_b:
        obj.option_b = "Đáp án B"

    if not obj.option_c:
        obj.option_c = "Đáp án C"

    if not obj.correct_answer:
        obj.correct_answer = "A"

    obj.save()

    if was_created:
        created += 1
    else:
        updated += 1

count_part1 = ListeningQuestion.objects.filter(part=1).count()
count_drive = ListeningQuestion.objects.filter(part=1).exclude(audio_drive_file_id="").count()

print("=" * 70)
print("IMPORT DONE")
print("=" * 70)
print("Created:", created)
print("Updated:", updated)
print("Part 1 total:", count_part1)
print("Part 1 with Drive audio:", count_drive)
print("Open admin:")
print("http://127.0.0.1:8000/admin/core/listeningquestion/")
