
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

def extract_topic_blocks(raw):
    raw = re.sub(r"(?i)\btopic\s*(\d+)([A-D])\s*:", r"topic \1 \2:", raw)
    matches = list(re.finditer(r"(?i)\btopic\s+(\d+)\s*:?", raw))
    blocks = {}
    for i, m in enumerate(matches):
        no = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        blocks[no] = raw[start:end].strip()
    return blocks

def extract_persons(block):
    pattern = re.compile(r"(?is)(?:Person\s*)?([A-D])\s*:\s*")
    matches = list(pattern.finditer(block))
    persons = {}
    for i, m in enumerate(matches):
        label = m.group(1).upper()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        text = block[start:end].strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if text:
            persons[label] = text
    return persons

def format_voice_info(persons):
    out = []
    for label in ["A", "B", "C", "D"]:
        if persons.get(label):
            out.append(f"Person {label}: {persons[label]}")
    return "\n\n".join(out).strip()

print("")
print("=== KIỂM TRA HIỆN TẠI ===")
for no, title in TOPIC_MAP.items():
    topic = Part2Topic.objects.filter(version="gioi", title=title).first()
    length = len(topic.voice_info.strip()) if topic and getattr(topic, "voice_info", "") else 0
    print(f"Topic {no}: {title} | voice_info: {length} ký tự")

print("")
print("=== DÁN LẠI KHỐI THÔNG TIN 12 TOPIC VÀO ĐÂY ===")
print("Dán xong gõ END rồi Enter.")
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
print("=== BẮT ĐẦU NHẬP LẠI ===")

for no, title in TOPIC_MAP.items():
    topic, _ = Part2Topic.objects.get_or_create(
        version="gioi",
        title=title,
        defaults={"description": "Chủ đề Mày giỏi"}
    )

    block = blocks.get(no, "").strip()
    persons = extract_persons(block)
    voice_info = format_voice_info(persons)

    if voice_info:
        topic.voice_info = voice_info
        topic.save()

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
        print(f"OK | Topic {no}: {title} | {len(persons)}/4 Person | {len(voice_info)} ký tự")
    else:
        print(f"CHƯA CÓ DỮ LIỆU | Topic {no}: {title}")

print("")
print("=== KIỂM TRA SAU KHI NHẬP ===")
for no, title in TOPIC_MAP.items():
    topic = Part2Topic.objects.filter(version="gioi", title=title).first()
    length = len(topic.voice_info.strip()) if topic and getattr(topic, "voice_info", "") else 0
    print(f"Topic {no}: {title} | voice_info: {length} ký tự")

print("")
print("XONG. Mở lại admin và bấm Ctrl + Shift + R.")
