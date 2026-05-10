
import os
import re
from difflib import get_close_matches

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Part2Topic, Part2Voice

CANONICAL_TOPICS = [
    "Topic Protect the environment",
    "Topic Protect the environment 2",
    "Topic Online shopping",
    "Topic Listening to music",
    "Topic Outdoor activities",
    "Topic The place to run",
    "Topic Do exercise",
    "Topic The internet",
    "Topic The Art",
    "Topic Travel to work.",
    "Topic Studying.",
    "Topic Studying phiên bản 2.",
]

def clean_topic_name(text):
    text = text.strip()

    # Xóa link nếu có dính vào tên
    text = re.sub(r"https?://\S+", "", text).strip()

    # Xóa đuôi file
    text = re.sub(r"\.(mp3|mp4|wav|m4a|aac|ogg)$", "", text, flags=re.I).strip()

    # Xóa phần đầu kiểu: 1,2, hoặc 1,12,
    text = re.sub(r"^\s*\d+\s*,\s*\d+\s*,\s*", "", text).strip()

    # Xóa số thứ tự đầu file: 2.Topic..., 12.Topic...
    text = re.sub(r"^\s*\d+\s*[\.\-_ ]+\s*", "", text).strip()

    # Xóa dấu chấm thừa đầu/cuối
    text = text.strip(" .\t\r\n")

    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()

    # Đảm bảo có chữ Topic ở đầu nếu tên đã bị lệch
    if not text.lower().startswith("topic "):
        text = "Topic " + text

    return text

def key(text):
    text = clean_topic_name(text).lower()
    text = text.replace("phiên", "phien").replace("bản", "ban")
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

canonical_by_key = {key(t): t for t in CANONICAL_TOPICS}

def match_topic(raw_name):
    k = key(raw_name)

    if k in canonical_by_key:
        return canonical_by_key[k]

    close = get_close_matches(k, canonical_by_key.keys(), n=1, cutoff=0.72)
    if close:
        return canonical_by_key[close[0]]

    return None

print("")
print("======================================================")
print("NHẬP AUDIO PART 2 - MÀY GIỎI")
print("======================================================")
print("Bạn dán dữ liệu đang có cũng được, hệ thống sẽ BỎ QUA part/question_number.")
print("Chỉ lấy: TÊN TOPIC + LINK DRIVE.")
print("Dán xong thì gõ END rồi Enter.")
print("")

lines = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    if line.strip():
        lines.append(line.strip())

matched = {}
unmatched = []

for line in lines:
    if "audio_drive_link" in line.lower():
        continue

    link_match = re.search(r"https?://\S+", line)
    if not link_match:
        continue

    link = link_match.group(0).strip()
    before_link = line[:link_match.start()].strip()

    # Lấy tên file/topic từ phần trước link, bỏ part/question_number
    topic_raw = clean_topic_name(before_link)
    topic_title = match_topic(topic_raw)

    if topic_title:
        matched[topic_title] = link
    else:
        unmatched.append((before_link, link))

print("")
print("======================================================")
print("KẾT QUẢ NHẬN DIỆN")
print("======================================================")

for title, link in matched.items():
    print(f"OK | Part 2 | {title} | {link}")

if unmatched:
    print("")
    print("Các dòng chưa nhận diện được:")
    for raw, link in unmatched:
        print(f"LỖI | {raw} | {link}")

print("")
print("======================================================")
print("ĐỒNG BỘ VÀO DATABASE LOCAL")
print("======================================================")

for title in CANONICAL_TOPICS:
    topic, _ = Part2Topic.objects.get_or_create(
        version="gioi",
        title=title,
        defaults={"description": "Chủ đề Mày giỏi"}
    )

    if title in matched:
        topic.audio_url = matched[title]

    topic.description = topic.description or "Chủ đề Mày giỏi"
    topic.save()

    # Mày giỏi: 1 file nghe chung + 4 Person chọn đáp án
    existing_orders = set(topic.voices.values_list("order", flat=True))

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

    status = "ĐÃ GẮN LINK" if title in matched else "CHƯA CÓ LINK"
    print(f"{status:12} | Part 2 | {title}")

print("")
print("======================================================")
print("TỔNG KẾT")
print("======================================================")
print(f"Đã nhận diện/gắn link: {len(matched)} / 12 topic")

missing = [t for t in CANONICAL_TOPICS if t not in matched]
if missing:
    print("")
    print("Topic chưa có link:")
    for t in missing:
        print("-", t)

print("")
print("XONG.")
print("Admin kiểm tra:")
print("http://127.0.0.1:8000/dashboard/part-2/may-gioi/")
print("")
print("Học viên kiểm tra:")
print("http://127.0.0.1:8000/listening/part-2/may-gioi/")
