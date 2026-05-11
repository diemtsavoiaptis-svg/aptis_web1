from pathlib import Path
import re

# ==================================================
# 1) BỔ SUNG FIELD CHO PART 2 MÀY GIỎI
# ==================================================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

# Add audio_url chung cho Part2Topic nếu thiếu
topic_block = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s)

if topic_block and "audio_url" not in topic_block.group(0):
    if "data_choices" in topic_block.group(0):
        s = re.sub(
            r"(data_choices\s*=\s*models\.TextField\([\s\S]*?\)\n)",
            r'\1    audio_url = models.URLField("Audio Drive chung", blank=True)\n',
            s,
            count=1
        )
    else:
        s = re.sub(
            r"(description\s*=\s*models\.TextField\([^\n]+\)\n)",
            r'\1    audio_url = models.URLField("Audio Drive chung", blank=True)\n',
            s,
            count=1
        )

# Add is_locked và question_text cho Part2Voice nếu thiếu
voice_block = re.search(r"class\s+Part2Voice\(models\.Model\):[\s\S]*?(?=\n#|\nclass |\Z)", s)

if voice_block:
    vb = voice_block.group(0)
    insert_lines = ""

    if "is_locked" not in vb:
        insert_lines += '    is_locked = models.BooleanField("Lock", default=False)\n'

    if "question_text" not in vb:
        insert_lines += '    question_text = models.TextField("Question", blank=True)\n'

    if insert_lines:
        s = re.sub(
            r"(class\s+Part2Voice\(models\.Model\):\s*\n)",
            r"\1" + insert_lines,
            s,
            count=1
        )

models.write_text(s, encoding="utf-8")


# ==================================================
# 2) GHI ĐÈ VIEW MÀY GIỎI THEO BỐ CỤC MỚI
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

# ===== Part 2 May Gioi final admin/student layout =====
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
    "Topic Studying version 2.",
]


def _is_admin_user_part2_gioi(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics():
    for title in PART2_GIOI_TOPICS:
        topic, created = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Version A Topic"}
        )

        existing_orders = set(topic.voices.values_list("order", flat=True))
        for i in range(1, 5):
            if i not in existing_orders:
                Part2Voice.objects.create(
                    topic=topic,
                    order=i,
                    question_text=f"Question {i}"
                )


def _ensure_four_gioi_rows(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Question {i}"
            )


@user_passes_test(_is_admin_user_part2_gioi)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")

    return render(request, "core/admin_part2_gioi_topics.html", {
        "topics": topics,
    })


@user_passes_test(_is_admin_user_part2_gioi)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_four_gioi_rows(topic)

    voices = list(topic.voices.all().order_by("order", "id"))

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"

            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = request.POST.get(prefix + "question_text", "").strip()
            voice.data_choices = request.POST.get(prefix + "data_choices", "").strip()
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()

            # Version A dùng 1 audio chung theo topic
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu data topics Version A.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "delete_topic":
        topic.delete()
        messages.success(request, "Đã xóa topics Version A.")
        return redirect("admin_part2_gioi_topics")

    rows = []
    for voice in voices:
        options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voices = list(topic.voices.all().order_by("order", "id"))

    rows = []
    for voice in voices:
        options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
    })
# ===== End Part 2 May Gioi final admin/student layout =====
'''

# Không xóa block cũ để tránh ảnh hưởng mày kém, định nghĩa mới ở cuối sẽ ghi đè function cùng tên.
if "Part 2 May Gioi final admin/student layout" not in v:
    v += block

views.write_text(v, encoding="utf-8")


# ==================================================
# 3) URLS
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

routes = [
    ('dashboard/part-2/may-gioi/', '    path("dashboard/part-2/may-gioi/", views.admin_part2_gioi_topics, name="admin_part2_gioi_topics"),'),
    ('dashboard/part-2/may-gioi/<int:topic_id>/', '    path("dashboard/part-2/may-gioi/<int:topic_id>/", views.admin_part2_gioi_detail, name="admin_part2_gioi_detail"),'),
    ('listening/part-2/may-gioi/<int:topic_id>/', '    path("listening/part-2/may-gioi/<int:topic_id>/", views.student_part2_gioi_page, name="student_part2_gioi"),'),
]

for key, route in routes:
    if key not in u:
        u = re.sub(
            r"urlpatterns\s*=\s*\[",
            "urlpatterns = [\n" + route,
            u,
            count=1
        )

urls.write_text(u, encoding="utf-8")


# ==================================================
# 4) TEMPLATE DANH SÁCH 12 CHỦ ĐỀ MÀY GIỎI
# ==================================================
Path("templates/core/admin_part2_gioi_topics.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Part 2 - Version A</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{
    --red:#e60023;
    --red2:#ff5f76;
    --deep:#7a0010;
    --dark:#3f0011;
    --line:#ffd1dc;
    --muted:#667085;
}
*{box-sizing:border-box}
body{
    margin:0;
    min-height:100vh;
    background:
        radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),
        linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
    font-family:"Segoe UI",Tahoma,Arial,sans-serif;
    color:var(--dark);
}
.wrap{
    max-width:1280px;
    margin:0 auto;
    padding:30px 20px 44px;
}
.hero{
    background:white;
    border:1px solid var(--line);
    border-radius:30px;
    padding:30px;
    box-shadow:0 18px 44px rgba(180,0,30,.07);
}
.badge{
    width:66px;
    height:66px;
    border-radius:21px;
    background:linear-gradient(135deg,var(--red),var(--red2));
    display:grid;
    place-items:center;
    color:white;
    font-size:30px;
    font-weight:950;
}
h1{
    margin:18px 0 8px;
    font-size:48px;
    letter-spacing:-.05em;
}
.desc{
    color:var(--muted);
    font-size:18px;
    line-height:1.65;
    font-weight:650;
}
.back{
    display:inline-flex;
    margin-top:18px;
    min-height:46px;
    padding:0 18px;
    border-radius:999px;
    background:#fff1f4;
    color:#8a0015;
    border:1px solid var(--line);
    text-decoration:none;
    font-weight:950;
}
.grid{
    margin-top:22px;
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:18px;
}
.topic{
    display:block;
    text-decoration:none;
    color:inherit;
    background:white;
    border:1px solid var(--line);
    border-radius:26px;
    padding:22px;
    box-shadow:0 16px 38px rgba(180,0,30,.06);
    transition:.16s ease;
}
.topic:hover{
    transform:translateY(-3px);
    box-shadow:0 22px 48px rgba(180,0,30,.11);
}
.num{
    width:42px;
    height:42px;
    border-radius:14px;
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    display:grid;
    place-items:center;
    font-weight:950;
}
.topic h2{
    margin:18px 0 10px;
    font-size:24px;
    line-height:1.2;
    letter-spacing:-.03em;
    color:#4a0010;
}
.topic p{
    color:var(--muted);
    line-height:1.55;
    font-weight:650;
}
.pill{
    display:inline-flex;
    min-height:34px;
    padding:0 12px;
    border-radius:999px;
    background:#fff1f4;
    border:1px solid #ffb6c2;
    color:#b8001c;
    font-weight:950;
}
@media(max-width:980px){
    .grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:620px){
    .grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<main class="wrap">
<section class="hero">
    <div class="badge">2</div>
    <h1>Part 2 - Version A</h1>
    <div class="desc">
        Có sẵn 12 topics. Click a topic to enter data admin: Lock, No., Question, Audio Drive, Answer đúng và Data answer.
    </div>
    <a class="back" href="/dashboard/part-2/">← Back to Version Selection</a>
</section>

<section class="grid">
{% for topic in topics %}
<a class="topic" href="/dashboard/part-2/may-gioi/{{ topic.id }}/">
    <div class="num">{{ forloop.counter }}</div>
    <h2>{{ topic.title }}</h2>
    <p>{{ topic.description|default:"Version A Topic" }}</p>
    <span class="pill">{{ topic.voices.count }} data rows</span>
</a>
{% endfor %}
</section>
</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 5) TEMPLATE ADMIN CHI TIẾT MÀY GIỎI
# ==================================================
Path("templates/core/admin_part2_gioi_detail.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ topic.title }} | Version A</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{
    --red:#e60023;
    --red2:#ff5f76;
    --deep:#7a0010;
    --dark:#3f0011;
    --line:#ffd1dc;
    --muted:#667085;
}
*{box-sizing:border-box}
body{
    margin:0;
    min-height:100vh;
    background:
        radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),
        linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
    font-family:"Segoe UI",Tahoma,Arial,sans-serif;
    color:var(--dark);
}
.wrap{
    max-width:1580px;
    margin:0 auto;
    padding:26px 18px 42px;
}
.hero,.card{
    background:white;
    border:1px solid var(--line);
    border-radius:28px;
    padding:24px;
    box-shadow:0 18px 44px rgba(180,0,30,.07);
}
.hero{
    display:flex;
    justify-content:space-between;
    gap:18px;
    align-items:flex-start;
}
h1{
    margin:0;
    font-size:38px;
    letter-spacing:-.04em;
}
.desc{
    margin-top:8px;
    color:var(--muted);
    line-height:1.6;
    font-weight:650;
}
.actions{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
}
.btn,.link{
    min-height:46px;
    border:0;
    border-radius:999px;
    padding:0 18px;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    text-decoration:none;
    font:inherit;
    font-weight:950;
    cursor:pointer;
}
.btn{
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    box-shadow:0 14px 28px rgba(230,0,35,.16);
}
.link{
    background:#fff1f4;
    color:#8a0015;
    border:1px solid var(--line);
}
.card{margin-top:16px}
label{
    display:block;
    margin-bottom:7px;
    color:var(--deep);
    font-weight:900;
}
input,textarea,select{
    width:100%;
    border:1px solid var(--line);
    border-radius:14px;
    padding:10px 12px;
    font:inherit;
    background:white;
    outline:none;
}
textarea{
    min-height:86px;
    resize:vertical;
}
input:focus,textarea:focus,select:focus{
    border-color:var(--red);
    box-shadow:0 0 0 4px rgba(230,0,35,.1);
}
.topic-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
}
.audio-box{
    margin-top:14px;
}
.note{
    margin-top:10px;
    padding:13px 15px;
    border-radius:16px;
    background:#fff1f4;
    border:1px solid var(--line);
    color:#8a0015;
    line-height:1.6;
    font-weight:750;
}
.table-wrap{
    overflow:auto;
    border:1px solid var(--line);
    border-radius:20px;
    margin-top:12px;
}
table{
    width:100%;
    min-width:1380px;
    border-collapse:collapse;
    background:white;
}
th{
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    padding:12px;
    text-align:left;
    font-weight:950;
    white-space:nowrap;
}
td{
    padding:10px;
    border-bottom:1px solid #ffe1e7;
    vertical-align:top;
}
tr:nth-child(even) td{background:#fffafa}
.lock-col{width:80px;text-align:center}
.stt-col{width:90px}
.question-col{min-width:280px}
.audio-col{min-width:260px}
.correct-col{min-width:260px}
.data-col{min-width:360px}
.message{
    margin-top:14px;
    padding:12px 16px;
    border-radius:16px;
    background:#ecfdf3;
    color:#027a48;
    font-weight:850;
}
.lock-check{
    width:22px;
    height:22px;
    accent-color:#e60023;
}
@media(max-width:900px){
    .hero{flex-direction:column}
    .topic-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<main class="wrap">

<section class="hero">
    <div>
        <h1>{{ topic.title }}</h1>
        <div class="desc">
            Admin Version A: mỗi topics có 1 file nghe chung. Bảng bên dưới dùng to enter questions, answer đúng và data answer.
        </div>
    </div>
    <div class="actions">
        <a class="link" href="/dashboard/part-2/may-gioi/">← Danh sách 12 topics</a>
        <a class="link" href="/listening/part-2/may-gioi/{{ topic.id }}/">View Student Interface</a>
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
        <label>Audio Drive chung của topics</label>
        <textarea name="audio_url" placeholder="Dán link Google Drive/audio. Version A Topic chỉ dùng 1 file nghe chung.">{{ topic.audio_url }}</textarea>

        {% if topic.audio_url %}
        <div class="note">
            Đã có link audio:
            <a href="{{ topic.audio_url }}" target="_blank" style="color:#b8001c;font-weight:950">Mở file nghe</a>
        </div>
        {% endif %}
    </div>
</section>

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Bảng data questions</h2>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Lock</th>
                    <th>No.</th>
                    <th>Question</th>
                    <th>Audio Drive</th>
                    <th>Answer đúng</th>
                    <th>Nhập data answer</th>
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
                            <textarea name="voice_{{ voice.id }}_question_text" placeholder="Nhập questions">{{ voice.question_text }}</textarea>
                        </td>

                        <td class="audio-col">
                            <div class="note" style="margin-top:0">
                                Dùng audio chung của topic.
                            </div>
                            <textarea readonly>{{ topic.audio_url }}</textarea>
                        </td>

                        <td class="correct-col">
                            <select name="voice_{{ voice.id }}_correct_data">
                                <option value="">-- Choose answer đúng --</option>
                                {% for option in row.options %}
                                    <option value="{{ option }}" {% if voice.correct_data == option %}selected{% endif %}>
                                        {{ option }}
                                    </option>
                                {% endfor %}
                            </select>

                            <div class="note">
                                Nếu chưa thấy lựa chọn, nhập data answer ở cột cuối rồi lưu trước.
                            </div>
                        </td>

                        <td class="data-col">
                            <textarea name="voice_{{ voice.id }}_data_choices" placeholder="Mỗi data answer một dòng">{{ voice.data_choices }}</textarea>
                        </td>
                    </tr>
                    {% endwith %}
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Save data topics</button>
    </div>
</section>
</form>

</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 6) TEMPLATE HỌC VIÊN MÀY GIỎI
# ==================================================
Path("templates/core/student_part2_gioi.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ topic.title }} | Part 2 Version A</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{
    --red:#e60023;
    --red2:#ff5f76;
    --deep:#7a0010;
    --dark:#3f0011;
    --line:#ffd1dc;
    --muted:#667085;
}
*{box-sizing:border-box}
body{
    margin:0;
    min-height:100vh;
    background:
        radial-gradient(circle at top right,rgba(255,95,118,.18),transparent 34%),
        linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
    font-family:"Segoe UI",Tahoma,Arial,sans-serif;
    color:var(--dark);
}
.wrap{
    max-width:1220px;
    margin:0 auto;
    padding:28px 20px 42px;
}
.exit{
    position:fixed;
    top:18px;
    right:22px;
    z-index:99;
    min-height:46px;
    padding:0 18px;
    border-radius:999px;
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    text-decoration:none;
    font-weight:950;
    box-shadow:0 14px 28px rgba(230,0,35,.18);
    display:inline-flex;
    align-items:center;
}
.topbar{
    border-left:4px solid var(--red);
    background:linear-gradient(90deg,#fff1f4,#fff7f9);
    border-radius:0 14px 14px 0;
    padding:14px 18px;
    font-weight:950;
    color:var(--deep);
    box-shadow:0 10px 24px rgba(180,0,30,.06);
}
.topic-card{
    margin-top:16px;
    background:white;
    border:1px solid var(--line);
    border-radius:24px;
    padding:24px;
    box-shadow:0 18px 40px rgba(180,0,30,.07);
}
h1{
    margin:0;
    font-size:38px;
    letter-spacing:-.04em;
    color:#3f0011;
}
.audio-box{
    margin-top:18px;
    border:1px solid #ffe1e7;
    background:#fff1f4;
    border-radius:18px;
    padding:18px;
}
.audio-title{
    font-weight:950;
    color:#7a0010;
    margin-bottom:10px;
}
.audio-link{
    display:inline-flex;
    align-items:center;
    min-height:44px;
    padding:0 16px;
    border-radius:999px;
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    text-decoration:none;
    font-weight:950;
}
.question-list{
    margin-top:16px;
    display:grid;
    gap:12px;
}
.q-card{
    border:1px solid var(--line);
    border-radius:18px;
    background:white;
    box-shadow:0 16px 38px rgba(180,0,30,.055);
    padding:18px;
    display:grid;
    grid-template-columns:1fr 260px;
    gap:14px;
    align-items:center;
}
.q-left{
    display:grid;
    grid-template-columns:44px 1fr;
    gap:14px;
}
.num{
    width:38px;
    height:38px;
    border-radius:50%;
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
    font-weight:950;
    display:grid;
    place-items:center;
}
.q-title{
    font-weight:950;
    font-size:20px;
}
.q-sub{
    margin-top:5px;
    color:var(--muted);
    font-weight:650;
}
select{
    width:100%;
    height:48px;
    border-radius:14px;
    border:1px dashed #f0aeb8;
    background:white;
    color:var(--muted);
    padding:0 13px;
    font-size:15px;
    font-weight:750;
}
.actions{
    margin-top:18px;
    display:flex;
    justify-content:flex-end;
    gap:10px;
}
.btn{
    min-width:128px;
    height:52px;
    border-radius:12px;
    border:0;
    padding:0 22px;
    font-size:17px;
    font-weight:950;
    cursor:pointer;
}
.submit{
    background:linear-gradient(135deg,var(--red),var(--red2));
    color:white;
}
@media(max-width:820px){
    .q-card{grid-template-columns:1fr}
    .wrap{padding-top:78px}
}
</style>
</head>
<body>
<a class="exit" href="/listening/">← Exit bài</a>

<main class="wrap">
<section class="topbar">Part 2 - Version A</section>

<section class="topic-card">
    <h1>{{ topic.title }}</h1>

    <div class="audio-box">
        <div class="audio-title">File nghe của topics</div>
        {% if topic.audio_url %}
            <a class="audio-link" href="{{ topic.audio_url }}" target="_blank">▶ Mở file nghe</a>
        {% else %}
            <div style="color:#8a0015;font-weight:800">Chưa có file nghe cho topics này.</div>
        {% endif %}
    </div>
</section>

<section class="question-list">
{% for row in rows %}
{% with voice=row.voice %}
<article class="q-card">
    <div class="q-left">
        <div class="num">{{ voice.order }}</div>
        <div>
            <div class="q-title">{{ voice.question_text|default:"Question chưa nhập" }}</div>
            <div class="q-sub">Choose answer phù hợp từ danh sách.</div>
        </div>
    </div>

    <select>
        <option>Choose answer...</option>
        {% for option in row.options %}
            <option>{{ option }}</option>
        {% endfor %}
    </select>
</article>
{% endwith %}
{% endfor %}
</section>

<section class="actions">
    <button class="btn submit" type="button">Submit</button>
</section>
</main>
</body>
</html>
''', encoding="utf-8")

print("DA_TAO_BO_CUC_PART2_MAY_GIOI_12_CHU_DE")
