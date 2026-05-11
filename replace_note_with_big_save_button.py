from pathlib import Path
import re

# ==================================================
# 1) Ghi đè view Version A: hỗ trợ nút "Save answer tổng"
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.shortcuts import render, redirect, get_object_or_404",
    "from django.contrib import messages",
]
for imp in imports:
    if imp not in s:
        s = imp + "\n" + s

if "Part2Topic" not in s or "Part2Voice" not in s:
    if "from .models import" in s:
        s = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic, Part2Voice",
            s,
            count=1
        )
    else:
        s = "from .models import Part2Topic, Part2Voice\n" + s

block = r'''

# ===== FINAL OVERRIDE May Gioi save total answers button =====
def _is_admin_user_part2_gioi_save_total(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_save_total(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_total_options_save_total(topic):
    return [
        x.strip()
        for x in (topic.data_choices or "").splitlines()
        if x.strip()
    ]


@user_passes_test(_is_admin_user_part2_gioi_save_total)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_save_total(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.save()

        for voice in voices:
            voice.question_text = f"Person {voice.order}"
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu answer tổng. Bây giờ có thể chọn answer đúng cho Person 1-4.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_correct_answers":
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

    options = _gioi_total_options_save_total(topic)

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
    _ensure_gioi_four_person_save_total(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_total_options_save_total(topic)

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
# ===== END FINAL OVERRIDE May Gioi save total answers button =====
'''

if "FINAL OVERRIDE May Gioi save total answers button" not in s:
    s += block

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) Ghi đè template admin Version A: có nút Save answer tổng to rõ
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
tpl.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ topic.title }} | Version A</title>
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
.save-total-btn{
    width:100%;
    min-height:64px;
    margin-top:16px;
    border:0;
    border-radius:18px;
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
    font-size:22px;
    font-weight:950;
    cursor:pointer;
    box-shadow:0 18px 34px rgba(230,0,35,.20);
}
.save-total-btn:hover{filter:brightness(.97);transform:translateY(-1px)}
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
.fixed-person{min-height:54px;display:flex;align-items:center;font-size:22px;font-weight:900;color:#111827;padding:12px 14px;border:1px solid #ffd1dc;border-radius:14px;background:#fffafa}
@media(max-width:900px){.hero{flex-direction:column}.topic-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">

<section class="hero">
    <div>
        <h1>{{ topic.title }}</h1>
        <div class="desc">
            Version A: <b>1 file nghe chung</b> + <b>4 Person</b>. Nhập data answer tổng trước, sau đó chọn answer đúng bên dưới.
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
<input type="hidden" name="action" value="save_total_answers">

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
        <textarea name="audio_url" placeholder="Dán 1 link audio Google Drive duy nhất cho topics này">{{ topic.audio_url }}</textarea>

        {% if topic.audio_url %}
        <div class="note">
            Đã có link audio:
            <a href="{{ topic.audio_url }}" target="_blank" style="color:#b8001c;font-weight:950">Mở file nghe</a>
        </div>
        {% endif %}
    </div>

    <div class="data-box">
        <label>Data answer tổng</label>
        <textarea name="data_choices" placeholder="Nhập data answer, mỗi answer một dòng. Ví dụ:
A
D
F
G">{{ topic.data_choices }}</textarea>
    </div>

    <button class="save-total-btn" type="submit">💾 Save answer tổng</button>
</section>
</form>

<form method="post">
{% csrf_token %}
<input type="hidden" name="action" value="save_correct_answers">

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Choose answer đúng cho 4 Person</h2>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Lock</th>
                    <th>No.</th>
                    <th>Person</th>
                    <th>Answer đúng</th>
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
                            <div class="fixed-person">Person {{ voice.order }}</div>
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

                            {% if not row.options %}
                            <div class="note">
                                Chưa có lựa chọn. Hãy nhập data answer tổng ở phía trên rồi bấm <b>Save answer tổng</b>.
                            </div>
                            {% endif %}
                        </td>
                    </tr>
                    {% endwith %}
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Save answer đúng</button>
    </div>
</section>
</form>

</main>
</body>
</html>
''', encoding="utf-8")

print("DA_THAY_DONG_NOTE_THANH_NUT_LUU_DAP_AN_TONG_TO_DUNG")
