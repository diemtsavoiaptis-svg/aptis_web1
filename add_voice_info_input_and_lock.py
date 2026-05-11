from pathlib import Path
import re

# ==================================================
# 1) Add field khóa voice_info vào Part2Topic
# ==================================================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

topic_block = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s)
if not topic_block:
    raise SystemExit("KHONG_TIM_THAY_CLASS_Part2Topic")

block = topic_block.group(0)

if "voice_info_locked" not in block:
    if "voice_info" in block:
        s = re.sub(
            r'(voice_info\s*=\s*models\.TextField\([^\n]+\)\n)',
            r'\1    voice_info_locked = models.BooleanField("Lock information voice", default=False)\n',
            s,
            count=1
        )
    else:
        s = re.sub(
            r'(audio_url\s*=\s*models\.URLField\([^\n]+\)\n)',
            r'\1    voice_info = models.TextField("Information của voice", blank=True)\n    voice_info_locked = models.BooleanField("Lock information voice", default=False)\n',
            s,
            count=1
        )

models.write_text(s, encoding="utf-8")


# ==================================================
# 2) Ghi đè view Version A: lưu/khoá/mở khóa voice_info
# ==================================================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

for imp in [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.shortcuts import render, redirect, get_object_or_404",
    "from django.contrib import messages",
]:
    if imp not in v:
        v = imp + "\n" + v

if "Part2Topic" not in v or "Part2Voice" not in v:
    if "from .models import" in v:
        v = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic, Part2Voice",
            v,
            count=1
        )
    else:
        v = "from .models import Part2Topic, Part2Voice\n" + v

override = r'''

# ===== FINAL: May Gioi voice info input + lock =====
def _is_admin_user_part2_gioi_voice_lock(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_voice_lock(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i, question_text=f"Person {i}")

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_options_voice_lock(topic):
    return [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]


@user_passes_test(_is_admin_user_part2_gioi_voice_lock)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_lock(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_total_answers":
            topic.title = request.POST.get("title", "").strip() or topic.title
            topic.description = request.POST.get("description", "").strip()
            topic.audio_url = request.POST.get("audio_url", "").strip()
            topic.data_choices = request.POST.get("data_choices", "").strip()

            # Chỉ cập nhật voice_info nếu chưa khóa
            if not getattr(topic, "voice_info_locked", False):
                topic.voice_info = request.POST.get("voice_info", "").strip()

            topic.save()

            for voice in voices:
                voice.question_text = f"Person {voice.order}"
                voice.audio_url = topic.audio_url
                voice.save()

            messages.success(request, "Đã lưu answer tổng.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "save_and_lock_voice_info":
            if not getattr(topic, "voice_info_locked", False):
                topic.voice_info = request.POST.get("voice_info", "").strip()
                topic.voice_info_locked = True
                topic.save()
                messages.success(request, "Đã lưu và khóa information voice.")
            else:
                messages.warning(request, "Information voice đang bị khóa.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "unlock_voice_info":
            topic.voice_info_locked = False
            topic.save()
            messages.success(request, "Đã mở khóa information voice. Bây giờ có thể sửa lại.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "save_correct_answers":
            for voice in voices:
                prefix = f"voice_{voice.id}_"
                voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
                voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
                voice.question_text = f"Person {voice.order}"
                voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
                voice.audio_url = topic.audio_url
                voice.save()

            messages.success(request, "Đã lưu answer đúng cho 4 Person.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _gioi_options_voice_lock(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_lock(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_options_voice_lock(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL: May Gioi voice info input + lock =====
'''

if "FINAL: May Gioi voice info input + lock" not in v:
    v += override

views.write_text(v, encoding="utf-8")


# ==================================================
# 3) Edit template admin: ô voice_info nhập được + nút lưu khóa
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# Delete block Information voice cũ nếu có
t = re.sub(
    r'\s*<section class="card voice-info-box">[\s\S]*?</section>\s*',
    '\n',
    t,
    flags=re.S
)

voice_block = r'''
<section class="card voice-info-box">
    <h2 class="voice-info-title">Information của voice</h2>
    <label>Nhập nguyên đoạn information Person A/B/C/D vào đây</label>

    <textarea
        name="voice_info"
        placeholder="Ví dụ:
topic 1 Person A: ...
Person B: ...
Person C: ...
Person D: ..."
        {% if topic.voice_info_locked %}readonly{% endif %}
    >{{ topic.voice_info|default_if_none:"" }}</textarea>

    {% if topic.voice_info_locked %}
        <div class="note">🔒 Information voice đã được khóa. Student sẽ xem phần này bằng nút Hiển thị / Ẩn information voice.</div>
        <button class="unlock-voice-btn" name="action" value="unlock_voice_info" type="submit">🔓 Open khóa information voice</button>
    {% else %}
        <button class="lock-voice-btn" name="action" value="save_and_lock_voice_info" type="submit">💾 Save & khóa information voice</button>
    {% endif %}
</section>
'''

# Chèn block vào trong form đầu tiên, sau nút lưu answer tổng
if "Save & khóa information voice" not in t:
    t = t.replace(
        '</section>\n</form>\n\n<form method="post">',
        '</section>\n' + voice_block + '\n</form>\n\n<form method="post">',
        1
    )

# CSS
if ".lock-voice-btn" not in t:
    t = t.replace("</style>", """
.voice-info-box{
    margin-top:16px;
    background:#fff;
    border:1px solid #ffd1dc;
    border-radius:22px;
    padding:18px;
    box-shadow:0 12px 26px rgba(180,0,30,.045);
}
.voice-info-title{
    margin:0 0 12px;
    color:#4a0010;
    font-size:22px;
    font-weight:950;
}
.voice-info-box textarea{
    min-height:260px;
    background:#fff;
    white-space:pre-wrap;
}
.voice-info-box textarea[readonly]{
    background:#fff6f8;
    color:#6b0014;
    cursor:not-allowed;
}
.lock-voice-btn,
.unlock-voice-btn{
    width:100%;
    min-height:58px;
    margin-top:14px;
    border:0;
    border-radius:18px;
    font-size:20px;
    font-weight:950;
    cursor:pointer;
}
.lock-voice-btn{
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
    box-shadow:0 16px 30px rgba(230,0,35,.18);
}
.unlock-voice-btn{
    background:#fff1f4;
    color:#9f0018;
    border:1px solid #ffb6c2;
}
</style>""")

tpl.write_text(t, encoding="utf-8")

print("DA_THEM_O_NHAP_VOICE_INFO_VA_KHOA_LAI")
