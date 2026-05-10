
import os
import csv
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import ListeningQuestion

print("Dán dữ liệu 32 câu Part 1 vào đây.")
print("Mỗi dòng theo dạng: STT[TAB]Câu hỏi[TAB]Đáp án A[TAB]Đáp án B[TAB]Đáp án C[TAB]voice/transcript")
print("Dán xong thì gõ END rồi bấm Enter.")
print("-" * 80)

lines = []
while True:
    line = input()
    if line.strip() == "END":
        break
    if line.strip():
        lines.append(line)

raw = "\n".join(lines)
Path("part1_32_import.tsv").write_text(raw, encoding="utf-8")

created = 0
updated = 0
skipped = 0

reader = csv.reader(raw.splitlines(), delimiter="\t")

for row in reader:
    if len(row) < 6:
        skipped += 1
        continue

    try:
        stt = int(str(row[0]).strip())
    except ValueError:
        skipped += 1
        continue

    if not (1 <= stt <= 32):
        skipped += 1
        continue

    cau_hoi = str(row[1]).strip()
    dap_an_a = str(row[2]).strip()
    dap_an_b = str(row[3]).strip()
    dap_an_c = str(row[4]).strip()
    voice_text = str(row[5]).strip()

    if voice_text.lower() in {"ko có", "không có", "khong co", "none", "null"}:
        voice_text = ""

    q, was_created = ListeningQuestion.objects.get_or_create(
        part=1,
        question_number=stt,
        defaults={
            "question_text": "",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "correct_answer": "A",
            "listening_transcript": "",
        },
    )

    q.question_text = cau_hoi
    q.option_a = dap_an_a
    q.option_b = dap_an_b
    q.option_c = dap_an_c
    q.listening_transcript = voice_text

    if not q.correct_answer:
        q.correct_answer = "A"

    q.save()

    if was_created:
        created += 1
    else:
        updated += 1

existing = set(
    ListeningQuestion.objects
    .filter(part=1, question_number__gte=1, question_number__lte=32)
    .values_list("question_number", flat=True)
)

missing = [i for i in range(1, 33) if i not in existing]

print("-" * 80)
print(f"IMPORT_PART1_32_DONE created={created} updated={updated} skipped={skipped}")
print("MISSING_1_TO_32:", missing)

if not missing:
    print("OK: Đã có đủ câu 1 đến câu 32.")
else:
    print("CẢNH BÁO: Còn thiếu câu:", missing)
