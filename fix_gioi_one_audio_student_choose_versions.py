from pathlib import Path
import re

# ==================================================
# 1) Đảm bảo model có field cần thiết
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
        ("kem", "Mày dốt"),
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
# 2) Ghi đè view Part 2: admin mày giỏi 1 audio tổng,
#    học viên có màn chọn Mày giỏi / Mày dốt
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

# ===== Part 2 final clean: admin gioi one audio, student choose version =====
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


def _is_admin_user_part2_final(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics_final():
    for title in PART2_GIOI_TOPICS:
        topic, _ = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        # Mày giỏi chỉ được có 1 voice tổng
        topic.voices.exclude(order=1).delete()

        voice, _ = Part2Voice.objects.get_or_create(
            topic=topic,
            order=1,
            defaults={"question_text": "Câu hỏi tổng"}
        )

        if not voice.question_text:
            voice.question_text = "Câu hỏi tổng"
            voice.save()


def _get_part2_gioi_total_voice(topic):
    topic.voices.exclude(order=1).delete()
    voice, _ = Part2Voice.objects.get_or_create(
        topic=topic,
        order=1,
        defaults={"question_text": "Câu hỏi tổng"}
    )
    return voice


@user_passes_test(_is_admin_user_part2_final)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics_final()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/admin_part2_gioi_topics.html", {"topics": topics})


@user_passes_test(_is_admin_user_part2_final)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_part2_gioi_total_voice(topic)

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.save()

        voice.is_locked = request.POST.get("voice_is_locked") == "on"
        voice.order = 1
        voice.question_text = request.POST.get("question_text", "").strip()
        voice.data_choices = request.POST.get("data_choices", "").strip()
        voice.correct_data = request.POST.get("correct_data", "").strip()
        voice.audio_url = topic.audio_url
        voice.save()

        messages.success(request, "Đã lưu dữ liệu Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })


def student_part2_page(request):
    return render(request, "core/student_part2_choose_version.html")


def student_part2_gioi_topics(request):
    _seed_part2_gioi_topics_final()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày giỏi",
        "topics": topics,
        "back_url": "/listening/part-2/",
        "topic_url_prefix": "/listening/part-2/may-gioi/",
    })


def student_part2_dot_topics(request):
    topics = Part2Topic.objects.filter(version="kem").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày dốt",
        "topics": topics,
        "back_url": "/listening/part-2/",
        "topic_url_prefix": "/listening/part-2/may-dot/",
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_part2_gioi_total_voice(topic)
    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })


def student_part2_dot_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="kem")
    voices = list(topic.voices.all().order_by("order", "id"))
    return render(request, "core/listening_part2.html", {
        "topic": topic,
        "voices": voices,
    })
# ===== End Part 2 final clean =====
'''

# Thêm block mới ở cuối để override function cũ
if "Part 2 final clean: admin gioi one audio" not in v:
    v += block

views.write_text(v, encoding="utf-8")


# ==================================================
# 3) URLs
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

routes = [
    ('dashboard/part-2/may-gioi/', '    path("dashboard/part-2/may-gioi/", views.admin_part2_gioi_topics, name="admin_part2_gioi_topics"),'),
    ('dashboard/part-2/may-gioi/<int:topic_id>/', '    path("dashboard/part-2/may-gioi/<int:topic_id>/", views.admin_part2_gioi_detail, name="admin_part2_gioi_detail"),'),

    ('listening/part-2/', '    path("listening/part-2/", views.student_part2_page, name="student_part2"),'),
    ('listening/part-2/may-gioi/', '    path("listening/part-2/may-gioi/", views.student_part2_gioi_topics, name="student_part2_gioi_topics"),'),
    ('listening/part-2/may-gioi/<int:topic_id>/', '    path("listening/part-2/may-gioi/<int:topic_id>/", views.student_part2_gioi_page, name="student_part2_gioi"),'),
    ('listening/part-2/may-dot/', '    path("listening/part-2/may-dot/", views.student_part2_dot_topics, name="student_part2_dot_topics"),'),
    ('listening/part-2/may-dot/<int:topic_id>/', '    path("listening/part-2/may-dot/<int:topic_id>/", views.student_part2_dot_page, name="student_part2_dot"),'),
]

for key, route in routes:
    if key not in u:
        u = re.sub(r"urlpatterns\s*=\s*\[", "urlpatterns = [\n" + route, u, count=1)

urls.write_text(u, encoding="utf-8")


# ==================================================
# 4) Template admin Mày giỏi: chỉ 1 link audio tổng
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
.wrap{max-width:1450px;margin:0 auto;padding:26px 18px 42px}
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
.audio-box{margin-top:14px}
.note{margin-top:10px;padding:13px 15px;border-radius:16px;background:#fff1f4;border:1px solid var(--line);color:#8a0015;line-height:1.6;font-weight:750}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:20px;margin-top:12px}
table{width:100%;min-width:1240px;border-collapse:collapse;background:white}
th{background:linear-gradient(135deg,var(--red),var(--red2));color:white;padding:12px;text-align:left;font-weight:950;white-space:nowrap}
td{padding:10px;border-bottom:1px solid #ffe1e7;vertical-align:top}
.lock-col{width:80px;text-align:center}
.stt-col{width:90px}
.question-col{min-width:280px}
.audio-col{min-width:250px}
.correct-col{min-width:260px}
.data-col{min-width:360px}
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
        <div class="desc">Mày giỏi chỉ có <b>1 link audio tổng</b>. Không còn bảng 4 voice audio.</div>
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
</section>

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Dữ liệu 1 voice tổng</h2>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Khóa</th>
                    <th>STT</th>
                    <th>Câu hỏi</th>
                    <th>Audio Drive</th>
                    <th>Đáp án đúng</th>
                    <th>Nhập dữ liệu đáp án</th>
                </tr>
            </thead>

            <tbody>
                <tr>
                    <td class="lock-col">
                        <input class="lock-check" type="checkbox" name="voice_is_locked" {% if voice.is_locked %}checked{% endif %}>
                    </td>

                    <td class="stt-col">
                        <input name="voice_order" value="1" readonly>
                    </td>

                    <td class="question-col">
                        <textarea name="question_text" placeholder="Nhập câu hỏi tổng">{{ voice.question_text }}</textarea>
                    </td>

                    <td class="audio-col">
                        <div class="note" style="margin-top:0">Dùng audio chung bên trên.</div>
                        <textarea readonly>{{ topic.audio_url }}</textarea>
                    </td>

                    <td class="correct-col">
                        <select name="correct_data">
                            <option value="">-- Chọn đáp án đúng --</option>
                            {% for option in options %}
                                <option value="{{ option }}" {% if voice.correct_data == option %}selected{% endif %}>
                                    {{ option }}
                                </option>
                            {% endfor %}
                        </select>

                        <div class="note">
                            Nếu chưa thấy lựa chọn, nhập dữ liệu đáp án ở cột cuối rồi lưu trước.
                        </div>
                    </td>

                    <td class="data-col">
                        <textarea name="data_choices" placeholder="Mỗi dữ liệu đáp án một dòng">{{ voice.data_choices }}</textarea>
                    </td>
                </tr>
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
# 5) Giao diện học viên: chọn Mày giỏi / Mày dốt
# ==================================================
Path("templates/core/student_part2_choose_version.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Listening Part 2</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{--red:#e60023;--red2:#ff5f76;--deep:#7a0010;--dark:#3f0011;--line:#ffd1dc;--muted:#667085}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:var(--dark)}
.wrap{max-width:1120px;margin:0 auto;padding:34px 20px}
.hero{background:white;border:1px solid var(--line);border-radius:30px;padding:30px;box-shadow:0 18px 44px rgba(180,0,30,.07)}
.badge{width:70px;height:70px;border-radius:22px;background:linear-gradient(135deg,var(--red),var(--red2));color:white;display:grid;place-items:center;font-size:34px;font-weight:950}
h1{margin:18px 0 8px;font-size:50px;letter-spacing:-.05em}
.desc{font-size:18px;line-height:1.6;color:var(--muted);font-weight:650}
.grid{margin-top:22px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.card{display:block;text-decoration:none;color:inherit;background:white;border:1px solid var(--line);border-radius:28px;padding:30px;box-shadow:0 18px 44px rgba(180,0,30,.07);transition:.18s ease}
.card:hover{transform:translateY(-4px);box-shadow:0 24px 54px rgba(180,0,30,.12)}
.num{width:58px;height:58px;border-radius:18px;background:linear-gradient(135deg,var(--red),var(--red2));color:white;display:grid;place-items:center;font-size:24px;font-weight:950}
.card h2{font-size:40px;margin:22px 0 10px;letter-spacing:-.04em}
.card p{color:var(--muted);font-size:17px;line-height:1.65;font-weight:650}
.exit{display:inline-flex;margin-top:20px;min-height:46px;padding:0 18px;border-radius:999px;background:#fff1f4;border:1px solid var(--line);color:#8a0015;text-decoration:none;font-weight:950}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">
<section class="hero">
    <div class="badge">2</div>
    <h1>Listening Part 2</h1>
    <div class="desc">Chọn phiên bản bài làm trước khi vào danh sách chủ đề.</div>
    <a class="exit" href="/listening/">← Quay lại Listening</a>
</section>

<section class="grid">
    <a class="card" href="/listening/part-2/may-gioi/">
        <div class="num">1</div>
        <h2>Mày giỏi</h2>
        <p>Mỗi chủ đề có 1 file nghe tổng và 1 câu dữ liệu tổng.</p>
    </a>

    <a class="card" href="/listening/part-2/may-dot/">
        <div class="num">2</div>
        <h2>Mày dốt</h2>
        <p>Mỗi chủ đề có 4 voice, tương ứng 4 người/4 ý dữ liệu.</p>
    </a>
</section>
</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 6) Danh sách topic học viên sau khi chọn phiên bản
# ==================================================
Path("templates/core/student_part2_topic_list.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Part 2 - {{ version_title }}</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{--red:#e60023;--red2:#ff5f76;--dark:#3f0011;--line:#ffd1dc;--muted:#667085}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:var(--dark)}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px}
.hero,.topic{background:white;border:1px solid var(--line);border-radius:28px;padding:26px;box-shadow:0 18px 44px rgba(180,0,30,.07)}
h1{margin:0;font-size:44px;letter-spacing:-.05em}
.desc{margin-top:10px;color:var(--muted);font-size:17px;line-height:1.65;font-weight:650}
.back{display:inline-flex;margin-top:16px;min-height:44px;padding:0 16px;border-radius:999px;background:#fff1f4;color:#8a0015;border:1px solid var(--line);text-decoration:none;font-weight:950}
.grid{margin-top:20px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.topic{text-decoration:none;color:inherit;display:block}
.topic h2{margin:0;font-size:23px;color:#4a0010;letter-spacing:-.03em}
.topic p{color:var(--muted);line-height:1.55}
@media(max-width:920px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">
<section class="hero">
<h1>Part 2 - {{ version_title }}</h1>
<div class="desc">Chọn chủ đề để bắt đầu làm bài.</div>
<a class="back" href="{{ back_url }}">← Quay lại chọn phiên bản</a>
</section>

<section class="grid">
{% for topic in topics %}
<a class="topic" href="{{ topic_url_prefix }}{{ topic.id }}/">
    <h2>{{ topic.title }}</h2>
    <p>{{ topic.description|default:"Chủ đề luyện nghe" }}</p>
</a>
{% empty %}
<div class="topic">
    <h2>Chưa có chủ đề</h2>
    <p>Admin chưa nhập dữ liệu cho phiên bản này.</p>
</div>
{% endfor %}
</section>
</main>
</body>
</html>
''', encoding="utf-8")

print("DA_FEED_LAI_MAY_GIOI_1_AUDIO_VA_THEM_CHON_MAY_GIOI_MAY_DOT_CHO_HOC_VIEN")
