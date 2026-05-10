from pathlib import Path
import re

# ==================================================
# 1) Đảm bảo models có đủ field
# ==================================================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

topic_match = re.search(r"class\s+Part2Topic\(models\.Model\):\s*\n", s)
if not topic_match:
    raise SystemExit("KHONG_TIM_THAY_CLASS_Part2Topic")

topic_block = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s).group(0)

if "version = models.CharField" not in topic_block:
    insert = '''    VERSION_CHOICES = [
        ("gioi", "Mày giỏi"),
        ("kem", "Mày kém"),
    ]

    version = models.CharField("Phiên bản", max_length=20, choices=VERSION_CHOICES, default="gioi")
'''
    s = s[:topic_match.end()] + insert + s[topic_match.end():]

topic_block = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s).group(0)

if "audio_url" not in topic_block:
    s = re.sub(
        r"(description\s*=\s*models\.TextField\([^\n]+\)\n)",
        r'\1    audio_url = models.URLField("Audio Drive chung", blank=True)\n',
        s,
        count=1
    )

if "data_choices" not in topic_block:
    s = re.sub(
        r"(description\s*=\s*models\.TextField\([^\n]+\)\n)",
        r'''\1    data_choices = models.TextField(
        "Dữ liệu đáp án tổng",
        blank=True,
        help_text="Mỗi đáp án một dòng. 4 person sẽ chọn từ danh sách này."
    )
''',
        s,
        count=1
    )

voice_match = re.search(r"class\s+Part2Voice\(models\.Model\):\s*\n", s)
if not voice_match:
    raise SystemExit("KHONG_TIM_THAY_CLASS_Part2Voice")

voice_block = re.search(r"class\s+Part2Voice\(models\.Model\):[\s\S]*?(?=\n#|\nclass |\Z)", s).group(0)
insert_voice = ""

if "is_locked" not in voice_block:
    insert_voice += '    is_locked = models.BooleanField("Khóa", default=False)\n'
if "question_text" not in voice_block:
    insert_voice += '    question_text = models.TextField("Câu hỏi", blank=True)\n'
if "correct_data" not in voice_block:
    insert_voice += '    correct_data = models.TextField("Đáp án đúng", blank=True)\n'

if insert_voice:
    s = s[:voice_match.end()] + insert_voice + s[voice_match.end():]

models.write_text(s, encoding="utf-8")


# ==================================================
# 2) Ghi đè view Mày giỏi: 1 audio chung + 4 person/câu hỏi
# ==================================================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.shortcuts import render, redirect, get_object_or_404",
    "from django.contrib import messages",
]
for imp in imports:
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

block = r'''

# ===== Part 2 May Gioi final: 1 audio + 4 person questions =====
PART2_GIOI_TOPICS = [
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


def _is_admin_user_part2_gioi_4p(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics_4p():
    for title in PART2_GIOI_TOPICS:
        topic, _ = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        existing_orders = set(topic.voices.values_list("order", flat=True))
        for i in range(1, 5):
            if i not in existing_orders:
                Part2Voice.objects.create(
                    topic=topic,
                    order=i,
                    question_text=f"Person {i}"
                )

        # Mày giỏi chỉ giữ đúng 4 person
        topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()


def _ensure_gioi_four_persons(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()


@user_passes_test(_is_admin_user_part2_gioi_4p)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics_4p()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")

    return render(request, "core/admin_part2_gioi_topics.html", {
        "topics": topics,
    })


@user_passes_test(_is_admin_user_part2_gioi_4p)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_persons(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = request.POST.get(prefix + "question_text", "").strip() or f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu dữ liệu Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_persons(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== End Part 2 May Gioi final: 1 audio + 4 person questions =====
'''

if "Part 2 May Gioi final: 1 audio + 4 person questions" not in v:
    v += block

views.write_text(v, encoding="utf-8")


# ==================================================
# 3) Template admin Mày giỏi: 1 audio chung + 4 dropdown đáp án đúng
# ==================================================
Path("templates/core/admin_part2_gioi_detail.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ topic.title }} | Mày giỏi</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{--red:#e60023;--red2:#ff5f76;--deep:#7a0010;--dark:#3f0011;--line:#ffd1dc;--muted:#667085}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:var(--dark)}
.wrap{max-width:1480px;margin:0 auto;padding:26px 18px 42px}
.hero,.card{background:white;border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 18px 44px rgba(180,0,30,.07)}
.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}
h1{margin:0;font-size:38px;letter-spacing:-.04em}
.desc{margin-top:8px;color:var(--muted);line-height:1.6;font-weight:650}
.actions{display:flex;gap:10px;flex-wrap:wrap}
.btn,.link{min-height:46px;border:0;border-radius:999px;padding:0 18px;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;font:inherit;font-weight:950;cursor:pointer}
.btn{background:linear-gradient(135deg,var(--red),var(--red2));color:white;box-shadow:0 14px 28px rgba(230,0,35,.16)}
.link{background:#fff1f4;color:#8a0015;border:1px solid var(--line)}
.card{margin-top:16px}
label{display:block;margin-bottom:7px;color:var(--deep);font-weight:900}
input,textarea,select{width:100%;border:1px solid var(--line);border-radius:14px;padding:10px 12px;font:inherit;background:white;outline:none}
textarea{min-height:92px;resize:vertical}
input:focus,textarea:focus,select:focus{border-color:var(--red);box-shadow:0 0 0 4px rgba(230,0,35,.1)}
.topic-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.audio-box,.data-box{margin-top:14px}
.note{margin-top:10px;padding:13px 15px;border-radius:16px;background:#fff1f4;border:1px solid var(--line);color:#8a0015;line-height:1.6;font-weight:750}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:20px;margin-top:12px}
table{width:100%;min-width:980px;border-collapse:collapse;background:white}
th{background:linear-gradient(135deg,var(--red),var(--red2));color:white;padding:12px;text-align:left;font-weight:950;white-space:nowrap}
td{padding:12px;border-bottom:1px solid #ffe1e7;vertical-align:top}
tr:nth-child(even) td{background:#fffafa}
.lock-col{width:80px;text-align:center}
.stt-col{width:90px}
.question-col{min-width:300px}
.correct-col{min-width:360px}
.message{margin-top:14px;padding:12px 16px;border-radius:16px;background:#ecfdf3;color:#027a48;font-weight:850}
.lock-check{width:22px;height:22px;accent-color:#e60023}
@media(max-width:900px){.hero{flex-direction:column}.topic-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">

<section class="hero">
    <div>
        <h1>{{ topic.title }}</h1>
        <div class="desc">
            Mày giỏi: <b>1 file nghe chung</b> + <b>4 câu / 4 person</b>. Mỗi person chọn 1 đáp án đúng từ dữ liệu đáp án tổng.
        </div>
    </div>
    <div class="actions">
        <a class="link" href="/dashboard/part-2/may-gioi/">← Danh sách 12 chủ đề</a>
        <a class="link" href="/listening/part-2/may-gioi/{{ topic.id }}/">Xem giao diện học viên</a>
    </div>
</section>

{% for message in messages %}
    <div class="message">{{ message }}</div>
{% endfor %}

<form method="post">
{% csrf_token %}
<input type="hidden" name="action" value="save_topic">

<section class="card">
    <div class="topic-grid">
        <div>
            <label>Tên topic</label>
            <input name="title" value="{{ topic.title }}">
        </div>
        <div>
            <label>Mô tả</label>
            <input name="description" value="{{ topic.description }}">
        </div>
    </div>

    <div class="audio-box">
        <label>Audio Drive chung của chủ đề</label>
        <textarea name="audio_url" placeholder="Dán 1 link audio Google Drive duy nhất cho chủ đề này">{{ topic.audio_url }}</textarea>

        {% if topic.audio_url %}
        <div class="note">
            Đã có link audio:
            <a href="{{ topic.audio_url }}" target="_blank" style="color:#b8001c;font-weight:950">Mở file nghe</a>
        </div>
        {% endif %}
    </div>

    <div class="data-box">
        <label>Dữ liệu đáp án tổng</label>
        <textarea name="data_choices" placeholder="Nhập 4 lựa chọn, mỗi lựa chọn một dòng. Ví dụ:
To relax
While studying
While singing
After waking up">{{ topic.data_choices }}</textarea>
    </div>

    <div class="note">
        Sau khi nhập dữ liệu đáp án tổng, bấm lưu. Sau đó 4 ô “Đáp án đúng” bên dưới sẽ hiện 4 lựa chọn để chọn cho từng Person.
    </div>
</section>

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Khóa</th>
                    <th>STT</th>
                    <th>Câu hỏi / Person</th>
                    <th>Đáp án đúng</th>
                </tr>
            </thead>

            <tbody>
                {% for row in rows %}
                    {% with voice=row.voice %}
                    <tr>
                        <td class="lock-col">
                            <input class="lock-check" type="checkbox" name="voice_{{ voice.id }}_is_locked" {% if voice.is_locked %}checked{% endif %}>
                        </td>

                        <td class="stt-col">
                            <input name="voice_{{ voice.id }}_order" value="{{ voice.order }}">
                        </td>

                        <td class="question-col">
                            <textarea name="voice_{{ voice.id }}_question_text" placeholder="Person {{ voice.order }}">{{ voice.question_text }}</textarea>
                        </td>

                        <td class="correct-col">
                            <select name="voice_{{ voice.id }}_correct_data">
                                <option value="">-- Chọn đáp án đúng --</option>
                                {% for option in row.options %}
                                    <option value="{{ option }}" {% if voice.correct_data == option %}selected{% endif %}>
                                        {{ option }}
                                    </option>
                                {% endfor %}
                            </select>

                            <div class="note">
                                Person {{ voice.order }} chọn 1 trong 4 lựa chọn.
                            </div>
                        </td>
                    </tr>
                    {% endwith %}
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Lưu dữ liệu chủ đề</button>
    </div>
</section>
</form>

</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 4) Template học viên Mày giỏi: 1 audio chung + 4 person dropdown
# ==================================================
Path("templates/core/student_part2_gioi.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ topic.title }} | Part 2 Mày giỏi</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{--red:#e60023;--red2:#ff5f76;--deep:#7a0010;--dark:#3f0011;--line:#ffd1dc;--muted:#667085}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:var(--dark)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 42px}
.exit{position:fixed;top:18px;right:22px;z-index:99;min-height:46px;padding:0 18px;border-radius:999px;background:linear-gradient(135deg,var(--red),var(--red2));color:white;text-decoration:none;font-weight:950;box-shadow:0 14px 28px rgba(230,0,35,.18);display:inline-flex;align-items:center}
.topbar{border-left:4px solid var(--red);background:linear-gradient(90deg,#fff1f4,#fff7f9);border-radius:0 14px 14px 0;padding:14px 18px;font-weight:950;color:var(--deep);box-shadow:0 10px 24px rgba(180,0,30,.06)}
.card{margin-top:16px;background:white;border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 18px 40px rgba(180,0,30,.07)}
h1{margin:0;font-size:38px;letter-spacing:-.04em;color:#3f0011}
.audio-box{margin-top:18px;border:1px solid #ffe1e7;background:#fff1f4;border-radius:18px;padding:18px}
.audio-title{font-weight:950;color:#7a0010;margin-bottom:10px}
.audio-link{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:999px;background:linear-gradient(135deg,var(--red),var(--red2));color:white;text-decoration:none;font-weight:950}
.person-list{display:grid;gap:12px}
.person-row{display:grid;grid-template-columns:180px 1fr;gap:16px;align-items:center;padding:14px;border:1px solid #ffe1e7;border-radius:18px;background:#fffafa}
.person-name{font-weight:950;color:#4a0010}
select{width:100%;height:52px;border-radius:14px;border:1px solid #d7c685;background:white;color:#333;padding:0 13px;font-size:15px;font-weight:750}
.actions{margin-top:18px;display:flex;justify-content:flex-end}
.btn{min-width:128px;height:52px;border-radius:12px;border:0;padding:0 22px;font-size:17px;font-weight:950;cursor:pointer;background:linear-gradient(135deg,var(--red),var(--red2));color:white}
@media(max-width:820px){.wrap{padding-top:78px}.person-row{grid-template-columns:1fr}}
</style>
</head>
<body>
<a class="exit" href="/listening/part-2/may-gioi/">← Thoát bài</a>

<main class="wrap">
<section class="topbar">Part 2 - Mày giỏi</section>

<section class="card">
    <h1>{{ topic.title }}</h1>

    <div class="audio-box">
        <div class="audio-title">File nghe của chủ đề</div>
        {% if topic.audio_url %}
            <a class="audio-link" href="{{ topic.audio_url }}" target="_blank">▶ Mở file nghe</a>
        {% else %}
            <div style="color:#8a0015;font-weight:800">Chưa có file nghe cho chủ đề này.</div>
        {% endif %}
    </div>
</section>

<section class="card">
    <div class="person-list">
        {% for row in rows %}
            {% with voice=row.voice %}
            <div class="person-row">
                <div class="person-name">
                    {{ voice.question_text|default:"Person" }} 
                </div>

                <select>
                    <option>-- Select an answer --</option>
                    {% for option in row.options %}
                        <option>{{ option }}</option>
                    {% endfor %}
                </select>
            </div>
            {% endwith %}
        {% endfor %}
    </div>
</section>

<section class="actions">
    <button class="btn" type="button">Submit</button>
</section>
</main>
</body>
</html>
''', encoding="utf-8")

print("DA_SUA_MAY_GIOI_THANH_1_AUDIO_CHUNG_4_PERSON_CHON_DAP_AN")
