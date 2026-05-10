from pathlib import Path
import re

# ==================================================
# 1) Thêm model riêng cho Part 2 nếu chưa có
# ==================================================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

if "class Part2Topic" not in s:
    s += r'''

# ===== Listening Part 2 data models =====
class Part2Topic(models.Model):
    title = models.CharField("Tên chủ đề", max_length=255)
    description = models.TextField("Mô tả", blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Chủ đề Part 2"
        verbose_name_plural = "Chủ đề Part 2"
        ordering = ["-id"]

    def __str__(self):
        return self.title


class Part2Voice(models.Model):
    topic = models.ForeignKey(Part2Topic, on_delete=models.CASCADE, related_name="voices", verbose_name="Chủ đề")
    order = models.PositiveIntegerField("Thứ tự người nói", default=1)

    audio_url = models.URLField("File audio / Link audio", blank=True)
    answer_a = models.CharField("Đáp án A", max_length=255, blank=True)
    answer_b = models.CharField("Đáp án B", max_length=255, blank=True)
    answer_c = models.CharField("Đáp án C", max_length=255, blank=True)
    answer_d = models.CharField("Đáp án D", max_length=255, blank=True)

    transcript = models.TextField("Nội dung file ghi âm", blank=True)
    data_choices = models.TextField(
        "Dữ liệu đáp án",
        blank=True,
        help_text="Nhập nhiều ý dữ liệu, mỗi ý một dòng. Khi làm bài chỉ chọn 4 ý tương ứng 4 người."
    )

    correct_answer = models.CharField(
        "Đáp án đúng",
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        blank=True
    )

    class Meta:
        verbose_name = "Voice Part 2"
        verbose_name_plural = "Voice Part 2"
        ordering = ["topic_id", "order", "id"]

    def __str__(self):
        return f"{self.topic} - Voice {self.order}"
# ===== End Listening Part 2 data models =====
'''
    models.write_text(s, encoding="utf-8")
    print("DA_THEM_MODEL_PART2")
else:
    print("MODEL_PART2_DA_CO")


# ==================================================
# 2) Thêm admin model vào core/admin.py
# ==================================================
admin = Path("core/admin.py")
a = admin.read_text(encoding="utf-8", errors="ignore")

if "Part2Topic" not in a:
    if "from .models import" in a:
        a = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic, Part2Voice",
            a,
            count=1
        )
    else:
        a = "from .models import Part2Topic, Part2Voice\n" + a

    a += r'''

# ===== Admin Part 2 =====
class Part2VoiceInline(admin.TabularInline):
    model = Part2Voice
    extra = 4
    fields = (
        "order",
        "audio_url",
        "answer_a",
        "answer_b",
        "answer_c",
        "answer_d",
        "transcript",
        "data_choices",
        "correct_answer",
    )


@admin.register(Part2Topic)
class Part2TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "description")
    inlines = [Part2VoiceInline]


@admin.register(Part2Voice)
class Part2VoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "order", "correct_answer")
    list_filter = ("topic", "correct_answer")
    search_fields = ("topic__title", "transcript", "data_choices")
# ===== End Admin Part 2 =====
'''
    admin.write_text(a, encoding="utf-8")
    print("DA_THEM_ADMIN_PART2")
else:
    print("ADMIN_PART2_DA_CO")


# ==================================================
# 3) Thêm forms/view Part 2 admin riêng, đẹp hơn Django Admin
# ==================================================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

needed_imports = [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.shortcuts import render, redirect, get_object_or_404",
    "from django.contrib import messages",
]
for imp in needed_imports:
    if imp not in v:
        v = imp + "\n" + v

# Đảm bảo import model Part2
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

part2_views = r'''

# ===== Custom Admin Part 2 management =====
def _is_admin_user_part2(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(_is_admin_user_part2)
def admin_part2_questions(request):
    topics = Part2Topic.objects.all().order_by("-id")

    if request.method == "POST" and request.POST.get("action") == "create_topic":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if not title:
            messages.error(request, "Bạn cần nhập tên chủ đề.")
            return redirect("admin_part2_questions")

        topic = Part2Topic.objects.create(title=title, description=description)

        # Tạo sẵn 4 voice cho 4 người
        for i in range(1, 5):
            Part2Voice.objects.create(topic=topic, order=i)

        messages.success(request, "Đã tạo chủ đề Part 2.")
        return redirect("admin_part2_topic_detail", topic_id=topic.id)

    return render(request, "core/admin_part2_topics.html", {
        "topics": topics,
    })


@user_passes_test(_is_admin_user_part2)
def admin_part2_topic_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id)

    # Luôn đảm bảo có 4 voice chính
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i)

    voices = list(topic.voices.all().order_by("order", "id"))

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.audio_url = request.POST.get(prefix + "audio_url", "").strip()
            voice.answer_a = request.POST.get(prefix + "answer_a", "").strip()
            voice.answer_b = request.POST.get(prefix + "answer_b", "").strip()
            voice.answer_c = request.POST.get(prefix + "answer_c", "").strip()
            voice.answer_d = request.POST.get(prefix + "answer_d", "").strip()
            voice.transcript = request.POST.get(prefix + "transcript", "").strip()
            voice.data_choices = request.POST.get(prefix + "data_choices", "").strip()
            voice.correct_answer = request.POST.get(prefix + "correct_answer", "").strip()
            voice.save()

        messages.success(request, "Đã lưu dữ liệu chủ đề Part 2.")
        return redirect("admin_part2_topic_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "delete_topic":
        topic.delete()
        messages.success(request, "Đã xóa chủ đề Part 2.")
        return redirect("admin_part2_questions")

    return render(request, "core/admin_part2_topic_detail.html", {
        "topic": topic,
        "voices": voices,
    })
# ===== End Custom Admin Part 2 management =====
'''

# Xóa block cũ Part2 admin nếu có để tránh trùng function
v = re.sub(
    r"\n?# ===== Custom Admin Part 2 management =====[\s\S]*?# ===== End Custom Admin Part 2 management =====\n?",
    "\n",
    v
)

v += part2_views
views.write_text(v, encoding="utf-8")


# ==================================================
# 4) URLs Part 2 admin
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

routes = [
    ('dashboard/part-2/', '    path("dashboard/part-2/", views.admin_part2_questions, name="admin_part2_questions"),'),
    ('dashboard/part-2/<int:topic_id>/', '    path("dashboard/part-2/<int:topic_id>/", views.admin_part2_topic_detail, name="admin_part2_topic_detail"),'),
]

for key, route in routes:
    if key not in u:
        u = re.sub(r"urlpatterns\s*=\s*\[", "urlpatterns = [\n" + route, u, count=1)

urls.write_text(u, encoding="utf-8")


# ==================================================
# 5) Template danh sách chủ đề Part 2
# ==================================================
tpl_list = Path("templates/core/admin_part2_topics.html")
tpl_list.parent.mkdir(parents=True, exist_ok=True)

tpl_list.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Quản lý Part 2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
    <style>
        :root{
            --red:#e60023;
            --red2:#ff5f76;
            --deep:#7a0010;
            --dark:#3f0011;
            --soft:#fff1f4;
            --line:#ffd1dc;
            --muted:#667085;
        }
        *{box-sizing:border-box}
        body{
            margin:0;
            min-height:100vh;
            background:radial-gradient(circle at top right, rgba(255,95,118,.18), transparent 34%),
                       linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
            color:var(--dark);
            font-family:"Segoe UI",Tahoma,Arial,sans-serif;
        }
        .wrap{
            max-width:1240px;
            margin:0 auto;
            padding:30px 20px 42px;
        }
        .top{
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:18px;
            background:rgba(255,255,255,.92);
            border:1px solid var(--line);
            border-radius:28px;
            padding:28px;
            box-shadow:0 18px 44px rgba(180,0,30,.07);
        }
        .badge{
            display:inline-grid;
            place-items:center;
            width:64px;
            height:64px;
            border-radius:20px;
            background:linear-gradient(135deg,var(--red),var(--red2));
            color:white;
            font-size:30px;
            font-weight:950;
            box-shadow:0 16px 30px rgba(230,0,35,.18);
        }
        h1{
            margin:16px 0 8px;
            font-size:48px;
            line-height:1;
            letter-spacing:-.05em;
            font-weight:950;
        }
        .desc{
            color:var(--muted);
            font-size:18px;
            line-height:1.6;
            font-weight:650;
        }
        .back{
            display:inline-flex;
            align-items:center;
            justify-content:center;
            min-height:46px;
            padding:0 18px;
            border-radius:999px;
            background:#fff1f4;
            border:1px solid var(--line);
            color:#8a0015;
            text-decoration:none;
            font-weight:950;
            white-space:nowrap;
        }
        .card{
            margin-top:18px;
            background:rgba(255,255,255,.92);
            border:1px solid var(--line);
            border-radius:28px;
            padding:24px;
            box-shadow:0 18px 44px rgba(180,0,30,.07);
        }
        .form-grid{
            display:grid;
            grid-template-columns:1fr 1fr auto;
            gap:12px;
            align-items:end;
        }
        label{
            display:block;
            margin-bottom:7px;
            color:var(--deep);
            font-weight:900;
        }
        input, textarea{
            width:100%;
            border:1px solid var(--line);
            border-radius:16px;
            min-height:48px;
            padding:12px 15px;
            font:inherit;
            outline:none;
            background:white;
        }
        textarea{height:48px;resize:vertical}
        input:focus,textarea:focus{
            border-color:var(--red);
            box-shadow:0 0 0 4px rgba(230,0,35,.1);
        }
        .btn{
            min-height:48px;
            border:0;
            border-radius:16px;
            padding:0 20px;
            background:linear-gradient(135deg,var(--red),var(--red2));
            color:white;
            font-weight:950;
            font:inherit;
            cursor:pointer;
            box-shadow:0 14px 28px rgba(230,0,35,.17);
        }
        .topic-grid{
            margin-top:18px;
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:16px;
        }
        .topic{
            display:block;
            padding:22px;
            border:1px solid var(--line);
            border-radius:24px;
            background:#fffafa;
            color:inherit;
            text-decoration:none;
            transition:.16s ease;
        }
        .topic:hover{
            transform:translateY(-3px);
            box-shadow:0 16px 34px rgba(180,0,30,.1);
        }
        .topic-title{
            font-size:24px;
            font-weight:950;
            letter-spacing:-.03em;
            color:#4a0010;
            line-height:1.2;
        }
        .topic-meta{
            margin-top:12px;
            color:var(--muted);
            font-weight:700;
            line-height:1.55;
        }
        .pill{
            display:inline-flex;
            margin-top:16px;
            min-height:34px;
            padding:0 12px;
            border-radius:999px;
            align-items:center;
            background:#fff1f4;
            border:1px solid var(--line);
            color:#b8001c;
            font-weight:900;
        }
        .messages{margin-top:16px;display:grid;gap:10px}
        .message{
            padding:12px 16px;
            border-radius:16px;
            background:#ecfdf3;
            color:#027a48;
            font-weight:850;
            border:1px solid #abefc6;
        }
        .empty{
            padding:28px;
            border:1px dashed #ff9cac;
            border-radius:22px;
            color:var(--muted);
            line-height:1.7;
            font-size:17px;
        }
        @media(max-width:900px){
            .form-grid{grid-template-columns:1fr}
            .topic-grid{grid-template-columns:1fr}
            .top{flex-direction:column}
        }
    </style>
</head>
<body>
<main class="wrap">
    <section class="top">
        <div>
            <div class="badge">2</div>
            <h1>Quản lý Part 2</h1>
            <div class="desc">
                Hiển thị hàng loạt tên chủ đề. Bấm vào từng chủ đề để nhập audio, đáp án A/B/C/D, transcript và dữ liệu đáp án cho 4 người.
            </div>
        </div>
        <a class="back" href="/dashboard/listening-parts/">← Quay lại chọn Part</a>
    </section>

    {% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}

    <section class="card">
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="create_topic">
            <div class="form-grid">
                <div>
                    <label>Tên chủ đề mới</label>
                    <input name="title" placeholder="Ví dụ: When they like listening to music">
                </div>
                <div>
                    <label>Mô tả</label>
                    <textarea name="description" placeholder="Ghi chú ngắn cho chủ đề này..."></textarea>
                </div>
                <button class="btn" type="submit">Tạo chủ đề</button>
            </div>
        </form>
    </section>

    <section class="card">
        <h2 style="margin:0 0 16px;font-size:28px;color:#4a0010">Danh sách chủ đề</h2>

        {% if topics %}
            <div class="topic-grid">
                {% for topic in topics %}
                    <a class="topic" href="/dashboard/part-2/{{ topic.id }}/">
                        <div class="topic-title">{{ topic.title }}</div>
                        <div class="topic-meta">
                            {{ topic.description|default:"Chưa có mô tả" }}
                        </div>
                        <div class="pill">{{ topic.voices.count }} voice</div>
                    </a>
                {% endfor %}
            </div>
        {% else %}
            <div class="empty">
                Chưa có chủ đề Part 2 nào. Hãy tạo chủ đề đầu tiên ở ô bên trên.
            </div>
        {% endif %}
    </section>
</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 6) Template chi tiết chủ đề Part 2
# ==================================================
tpl_detail = Path("templates/core/admin_part2_topic_detail.html")
tpl_detail.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ topic.title }} | Part 2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
    <style>
        :root{
            --red:#e60023;
            --red2:#ff5f76;
            --deep:#7a0010;
            --dark:#3f0011;
            --soft:#fff1f4;
            --line:#ffd1dc;
            --muted:#667085;
        }
        *{box-sizing:border-box}
        body{
            margin:0;
            min-height:100vh;
            background:radial-gradient(circle at top right, rgba(255,95,118,.18), transparent 34%),
                       linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
            color:var(--dark);
            font-family:"Segoe UI",Tahoma,Arial,sans-serif;
        }
        .wrap{
            max-width:1520px;
            margin:0 auto;
            padding:28px 18px 42px;
        }
        .hero{
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:18px;
            background:rgba(255,255,255,.94);
            border:1px solid var(--line);
            border-radius:28px;
            padding:24px;
            box-shadow:0 18px 44px rgba(180,0,30,.07);
        }
        h1{
            margin:0;
            font-size:38px;
            letter-spacing:-.04em;
            color:#3f0011;
        }
        .hint{
            margin-top:8px;
            color:var(--muted);
            font-weight:650;
            line-height:1.6;
        }
        .actions{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        }
        .btn,.link-btn{
            min-height:46px;
            border:0;
            border-radius:999px;
            padding:0 18px;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            background:linear-gradient(135deg,var(--red),var(--red2));
            color:white;
            font:inherit;
            font-weight:950;
            cursor:pointer;
            text-decoration:none;
            box-shadow:0 14px 28px rgba(230,0,35,.16);
        }
        .light{
            background:#fff1f4;
            color:#8a0015;
            border:1px solid var(--line);
            box-shadow:none;
        }
        .danger{
            background:#fff1f4;
            color:#b8001c;
            border:1px solid #ff9cac;
            box-shadow:none;
        }
        .card{
            margin-top:16px;
            background:rgba(255,255,255,.94);
            border:1px solid var(--line);
            border-radius:24px;
            padding:20px;
            box-shadow:0 18px 44px rgba(180,0,30,.06);
        }
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
        textarea{min-height:92px;resize:vertical}
        input:focus,textarea:focus,select:focus{
            border-color:var(--red);
            box-shadow:0 0 0 4px rgba(230,0,35,.1);
        }
        .topic-grid{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:12px;
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
            background:linear-gradient(135deg,#e60023,#ff5f76);
            color:white;
            padding:12px;
            text-align:left;
            font-weight:950;
            white-space:nowrap;
            border-right:1px solid rgba(255,255,255,.18);
        }
        td{
            padding:10px;
            border-bottom:1px solid #ffe1e7;
            vertical-align:top;
        }
        tr:nth-child(even) td{background:#fffafa}
        .small-input{width:70px}
        .audio-cell{min-width:210px}
        .answer-cell{min-width:170px}
        .transcript-cell{min-width:260px}
        .data-cell{min-width:310px}
        .messages{margin-top:16px;display:grid;gap:10px}
        .message{
            padding:12px 16px;
            border-radius:16px;
            background:#ecfdf3;
            color:#027a48;
            font-weight:850;
            border:1px solid #abefc6;
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
            <div class="hint">
                Bảng dữ liệu Part 2: mỗi chủ đề có 4 voice tương ứng 4 người. Mỗi voice có audio, A/B/C/D, transcript và dữ liệu đáp án.
            </div>
        </div>
        <div class="actions">
            <a class="link-btn light" href="/dashboard/part-2/">← Danh sách chủ đề</a>
            <a class="link-btn light" href="/listening/part-2/">Xem giao diện học viên</a>
        </div>
    </section>

    {% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <input type="hidden" name="action" value="save_topic">

        <section class="card">
            <div class="topic-grid">
                <div>
                    <label>Tên chủ đề</label>
                    <input name="title" value="{{ topic.title }}">
                </div>
                <div>
                    <label>Mô tả / ghi chú</label>
                    <input name="description" value="{{ topic.description }}">
                </div>
            </div>

            <div class="note">
                Cột “Dữ liệu đáp án” có thể nhập nhiều dòng, nhưng khi làm bài chỉ khai thác 4 dữ liệu tương ứng 4 người.
            </div>
        </section>

        <section class="card">
            <h2 style="margin:0 0 8px;font-size:26px;color:#4a0010">Dữ liệu 4 voice</h2>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>File audio của chủ đề</th>
                            <th>Đáp án A</th>
                            <th>Đáp án B</th>
                            <th>Đáp án C</th>
                            <th>Đáp án D</th>
                            <th>Nội dung file ghi âm</th>
                            <th>Dữ liệu của các đáp án</th>
                            <th>Đáp án đúng</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for voice in voices %}
                        <tr>
                            <td>
                                <input class="small-input" name="voice_{{ voice.id }}_order" value="{{ voice.order }}">
                            </td>
                            <td class="audio-cell">
                                <textarea name="voice_{{ voice.id }}_audio_url" placeholder="Dán link audio hoặc file audio">{{ voice.audio_url }}</textarea>
                            </td>
                            <td class="answer-cell">
                                <textarea name="voice_{{ voice.id }}_answer_a" placeholder="Đáp án A">{{ voice.answer_a }}</textarea>
                            </td>
                            <td class="answer-cell">
                                <textarea name="voice_{{ voice.id }}_answer_b" placeholder="Đáp án B">{{ voice.answer_b }}</textarea>
                            </td>
                            <td class="answer-cell">
                                <textarea name="voice_{{ voice.id }}_answer_c" placeholder="Đáp án C">{{ voice.answer_c }}</textarea>
                            </td>
                            <td class="answer-cell">
                                <textarea name="voice_{{ voice.id }}_answer_d" placeholder="Đáp án D">{{ voice.answer_d }}</textarea>
                            </td>
                            <td class="transcript-cell">
                                <textarea name="voice_{{ voice.id }}_transcript" placeholder="Transcript / nội dung file ghi âm">{{ voice.transcript }}</textarea>
                            </td>
                            <td class="data-cell">
                                <textarea name="voice_{{ voice.id }}_data_choices" placeholder="Mỗi dữ liệu một dòng. Có thể nhập nhiều dòng, nhưng bài làm chỉ chọn 4 dữ liệu.">{{ voice.data_choices }}</textarea>
                            </td>
                            <td>
                                <select name="voice_{{ voice.id }}_correct_answer">
                                    <option value="">--</option>
                                    <option value="A" {% if voice.correct_answer == "A" %}selected{% endif %}>A</option>
                                    <option value="B" {% if voice.correct_answer == "B" %}selected{% endif %}>B</option>
                                    <option value="C" {% if voice.correct_answer == "C" %}selected{% endif %}>C</option>
                                    <option value="D" {% if voice.correct_answer == "D" %}selected{% endif %}>D</option>
                                </select>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="actions" style="justify-content:flex-end;margin-top:16px">
                <button class="btn" type="submit">Lưu dữ liệu chủ đề</button>
            </div>
        </section>
    </form>

    <form method="post" onsubmit="return confirm('Bạn chắc chắn muốn xóa toàn bộ chủ đề Part 2 này?');">
        {% csrf_token %}
        <input type="hidden" name="action" value="delete_topic">
        <section class="card">
            <button class="btn danger" type="submit">Xóa chủ đề này</button>
        </section>
    </form>
</main>
</body>
</html>
''', encoding="utf-8")

print("DA_TAO_ADMIN_PART2_THEO_YEU_CAU")
