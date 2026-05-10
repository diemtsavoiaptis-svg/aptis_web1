from pathlib import Path

Path("import_part2_gioi_voice_info_by_topic_number.py").write_text(r'''
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Part2Topic, Part2Voice


TOPIC_MAP = {
    1: "Topic Protect the environment",
    2: "Topic Protect the environment 2",
    3: "Topic Online shopping",
    4: "Topic Listening to music",
    5: "Topic Outdoor activities",
    6: "Topic The place to run",
    7: "Topic Do exercise",
    8: "Topic The internet",
    9: "Topic The Art",
    10: "Topic Travel to work.",
    11: "Topic Studying.",
    12: "Topic Studying phiên bản 2.",
}


def clean_text(text):
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_topic_blocks(raw):
    # Sửa trường hợp topic 5A: thành topic 5 A:
    raw = re.sub(r"(?i)\btopic\s*(\d+)([A-D])\s*:", r"topic \1 \2:", raw)

    # Nhận cả:
    # topic 1
    # topic 1:
    # Topic 1 Person A:
    matches = list(re.finditer(r"(?i)\btopic\s+(\d+)\s*:?", raw))

    blocks = {}

    for i, m in enumerate(matches):
        topic_no = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        blocks[topic_no] = raw[start:end].strip()

    return blocks


def extract_persons(block):
    # Nhận được cả:
    # Person A:
    # A:
    # topic 5 A:
    pattern = re.compile(r"(?is)(?:Person\s*)?([A-D])\s*:\s*")
    matches = list(pattern.finditer(block))

    persons = {}

    for i, m in enumerate(matches):
        label = m.group(1).upper()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        content = clean_text(block[start:end])
        if content:
            persons[label] = content

    return persons


def format_voice_info(persons):
    output = []
    for label in ["A", "B", "C", "D"]:
        text = persons.get(label, "").strip()
        if text:
            output.append(f"Person {label}: {text}")
    return "\n\n".join(output).strip()


print("")
print("====================================================")
print("NHẬP THÔNG TIN VOICE PART 2 - MÀY GIỎI")
print("====================================================")
print("Dán nguyên khối dữ liệu 12 topic vào đây.")
print("Hệ thống sẽ tự khớp theo số topic 1-12 để đúng với file nghe.")
print("Dán xong thì gõ END rồi Enter.")
print("")

lines = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)

raw = "\n".join(lines)
blocks = extract_topic_blocks(raw)

print("")
print("====================================================")
print("KIỂM TRA DỮ LIỆU ĐÃ ĐỌC")
print("====================================================")

updated = 0
missing = []
partial = []

for topic_no in range(1, 13):
    title = TOPIC_MAP[topic_no]
    block = blocks.get(topic_no, "").strip()

    topic, _ = Part2Topic.objects.get_or_create(
        version="gioi",
        title=title,
        defaults={"description": "Chủ đề Mày giỏi"}
    )

    if not block:
        missing.append((topic_no, title))
        print(f"THIẾU | Topic {topic_no}: {title}")
        continue

    persons = extract_persons(block)
    voice_info = format_voice_info(persons)

    if voice_info:
        topic.voice_info = voice_info
        topic.save()

        # Đảm bảo đúng 4 Person, khớp với 1 file nghe chung của topic
        for i in range(1, 5):
            voice, _ = Part2Voice.objects.get_or_create(
                topic=topic,
                order=i,
                defaults={"question_text": f"Person {i}"}
            )
            voice.question_text = f"Person {i}"
            voice.audio_url = topic.audio_url
            voice.save()

        topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

        updated += 1

        count = len(persons)
        if count < 4:
            partial.append((topic_no, title, count))
            print(f"THIẾU PERSON | Topic {topic_no}: {title} | đọc được {count}/4")
        else:
            print(f"OK | Topic {topic_no}: {title} | đủ {count}/4 Person")
    else:
        missing.append((topic_no, title))
        print(f"LỖI ĐỌC | Topic {topic_no}: {title}")


print("")
print("====================================================")
print("TỔNG KẾT")
print("====================================================")
print(f"Đã cập nhật: {updated}/12 topic")

if missing:
    print("")
    print("Topic chưa nhập/không đọc được:")
    for no, title in missing:
        print(f"- Topic {no}: {title}")

if partial:
    print("")
    print("Topic đọc chưa đủ 4 Person:")
    for no, title, count in partial:
        print(f"- Topic {no}: {title} | {count}/4 Person")

print("")
print("XONG.")
print("Admin kiểm tra:")
print("http://127.0.0.1:8000/dashboard/part-2/may-gioi/")
print("")
print("Học viên kiểm tra:")
print("http://127.0.0.1:8000/listening/part-2/may-gioi/")
''', encoding="utf-8")

print("DA_TAO_TOOL_NHAP_THONG_TIN_VOICE_KHOP_FILE_NGHE")
