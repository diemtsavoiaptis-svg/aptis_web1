from pathlib import Path

# =========================
# 1) forms.py: không bắt buộc email
# =========================
Path("core/forms.py").write_text(r'''from django import forms


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Họ và tên học viên",
            "autocomplete": "name",
        })
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Số điện thoại",
            "autocomplete": "tel",
        })
    )

    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Tài khoản hoặc email",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Mật khẩu",
            "autocomplete": "new-password",
        })
    )


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Tài khoản hoặc email",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Mật khẩu",
            "autocomplete": "current-password",
        })
    )
''', encoding="utf-8")


# =========================
# 2) listening_ui.py: context sạch cho giao diện học viên
# =========================
Path("core/listening_ui.py").write_text(r'''from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from .models import ListeningQuestion


def pick_value(obj, *names, default=""):
    for name in names:
        value = getattr(obj, name, None)
        if value not in [None, ""]:
            return value
    return default


@login_required
def listening_page(request):
    try:
        part_number = int(request.GET.get("part", 1))
    except Exception:
        part_number = 1

    try:
        current_index = int(request.GET.get("q", 1))
    except Exception:
        current_index = 1

    if part_number not in [1, 2, 3, 4]:
        part_number = 1

    questions = ListeningQuestion.objects.filter(part=part_number).order_by("question_number", "id")
    total_questions = questions.count()

    if total_questions == 0:
        return render(request, "core/listening.html", {
            "part_number": part_number,
            "part_tabs": [1, 2, 3, 4],
            "no_question": True,
            "total_questions": 0,
            "all_question_numbers": [],
        })

    if current_index < 1:
        current_index = 1
    if current_index > total_questions:
        current_index = total_questions

    current = questions[current_index - 1]

    question_text = pick_value(current, "question_text", "question", "title", default=f"Câu hỏi {current_index}")
    option_a = pick_value(current, "option_a", "answer_a", "choice_a", default="Đáp án A")
    option_b = pick_value(current, "option_b", "answer_b", "choice_b", default="Đáp án B")
    option_c = pick_value(current, "option_c", "answer_c", "choice_c", default="Đáp án C")
    correct_answer = pick_value(current, "correct_answer", "correct_option", "answer_key", default="A")
    transcript = pick_value(
        current,
        "listening_transcript",
        "transcript",
        "script_text",
        "listening_text",
        "explanation",
        "answer_explanation",
        default="Chưa có transcript.",
    )

    context = {
        "part_number": part_number,
        "part_tabs": [1, 2, 3, 4],
        "question": {
            "id": current.id,
            "prompt": question_text,
            "option_a": option_a,
            "option_b": option_b,
            "option_c": option_c,
            "correct_answer": str(correct_answer).strip().upper(),
            "transcript": transcript,
        },
        "audio_url": reverse("secure_audio", args=[current.id]),
        "current_index": current_index,
        "total_questions": total_questions,
        "progress_percent": round((current_index / total_questions) * 100, 2),
        "prev_url": f"{reverse('listening')}?part={part_number}&q={current_index - 1}" if current_index > 1 else "",
        "next_url": f"{reverse('listening')}?part={part_number}&q={current_index + 1}" if current_index < total_questions else "",
        "all_question_numbers": list(range(1, total_questions + 1)),
    }
    return render(request, "core/listening.html", context)
''', encoding="utf-8")


# =========================
# 3) dashboard.html: giao diện admin đỏ
# =========================
Path("templates/core/dashboard.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Admin | Điểm TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/app_red.css' %}">
</head>
<body class="admin-body">
<div class="admin-shell">
    <aside class="admin-sidebar">
        <div class="brand-block">
            <div class="brand-logo">A</div>
            <div>
                <div class="brand-name">Điểm TSA</div>
                <div class="brand-sub">với Aptis</div>
            </div>
        </div>

        <nav class="side-nav">
            <a class="active" href="{% url 'dashboard' %}">🎧 Tổng quan Admin</a>
            <a href="/admin/core/listeningquestion/">🎧 Quản lý câu hỏi Listening</a>
            <a href="/admin/core/studentprofile/">✅ Duyệt học viên</a>
            <a href="/admin/core/lesson/">📚 Quản lý bài học</a>
            <a href="/admin/core/securityalert/">🛡️ Cảnh báo bảo mật</a>
            <a href="{% url 'listening' %}">👀 Xem giao diện học viên</a>
            <a href="{% url 'logout' %}">🚪 Đăng xuất</a>
        </nav>
    </aside>

    <main class="admin-main">
        <header class="admin-header">
            <div>
                <p class="eyebrow">Dashboard quản trị</p>
                <h1>Xin chào, {{ request.user.username }}</h1>
                <p class="muted">Quản lý học viên, bài nghe và dữ liệu luyện thi Aptis.</p>
            </div>
            <a class="primary-btn" href="/admin/">Mở Django Admin</a>
        </header>

        <section class="stat-grid">
            <div class="stat-card">
                <span>🎧</span>
                <strong>Listening</strong>
                <p>Thêm/sửa câu hỏi, audio, đáp án và transcript.</p>
                <a href="/admin/core/listeningquestion/">Quản lý Listening →</a>
            </div>
            <div class="stat-card">
                <span>✅</span>
                <strong>Học viên</strong>
                <p>Duyệt tài khoản học viên mới đăng ký.</p>
                <a href="/admin/core/studentprofile/">Duyệt học viên →</a>
            </div>
            <div class="stat-card">
                <span>📚</span>
                <strong>Bài học</strong>
                <p>Quản lý tài liệu, mô tả và video học tập.</p>
                <a href="/admin/core/lesson/">Quản lý bài học →</a>
            </div>
        </section>

        <section class="content-card">
            <div class="section-head">
                <div>
                    <h2>Danh sách bài học</h2>
                    <p class="muted">Các bài học đang có trong hệ thống.</p>
                </div>
                <a class="ghost-btn" href="/admin/core/lesson/add/">+ Thêm bài học</a>
            </div>

            <div class="lesson-list">
                {% for lesson in lessons %}
                    <article class="lesson-item">
                        <h3>{{ lesson.title }}</h3>
                        <p>{{ lesson.description|default:"Chưa có mô tả." }}</p>
                        {% if lesson.video_url %}
                            <a href="{{ lesson.video_url }}" target="_blank">Xem video</a>
                        {% endif %}
                    </article>
                {% empty %}
                    <div class="empty-box">
                        Chưa có bài học nào. Bấm “Thêm bài học” để tạo nội dung đầu tiên.
                    </div>
                {% endfor %}
            </div>
        </section>
    </main>
</div>
</body>
</html>
''', encoding="utf-8")


# =========================
# 4) listening.html: giao diện học viên đỏ
# =========================
Path("templates/core/listening.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Listening Part {{ part_number }} | Điểm TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/app_red.css' %}">
</head>
<body class="student-body">
<div class="student-shell">
    <header class="student-top">
        <div class="brand-inline">
            <div class="brand-logo">A</div>
            <div>
                <strong>Điểm TSA Với Aptis</strong>
                <span>Listening Practice</span>
            </div>
        </div>
        <div class="student-actions">
            <a href="{% url 'dashboard' %}" class="ghost-btn">Trang chính</a>
            <a href="{% url 'logout' %}" class="ghost-btn">Đăng xuất</a>
        </div>
    </header>

    <main class="student-layout">
        <section class="exam-panel">
            <div class="exam-title">
                <div class="part-card">
                    <span>Part</span>
                    <strong>{{ part_number }}</strong>
                </div>
                <div>
                    <h1>Listening Practice</h1>
                    <p>Luyện nghe từng câu, rõ ràng và dễ thao tác.</p>
                </div>
            </div>

            <div class="part-tabs">
                {% for part in part_tabs %}
                    <a class="{% if part == part_number %}active{% endif %}" href="{% url 'listening' %}?part={{ part }}">Part {{ part }}</a>
                {% endfor %}
            </div>

            {% if no_question %}
                <div class="empty-box">
                    <h2>Chưa có dữ liệu Listening cho Part {{ part_number }}</h2>
                    <p>Admin cần nhập câu hỏi trong trang quản trị trước.</p>
                </div>
            {% else %}
                <div class="progress-wrap">
                    <div class="progress-info">
                        <strong>Câu {{ current_index }}/{{ total_questions }}</strong>
                        <span>{{ progress_percent }}%</span>
                    </div>
                    <div class="progress-bar">
                        <div style="width: {{ progress_percent }}%"></div>
                    </div>
                </div>

                <article class="question-card">
                    <div class="question-head">
                        <span class="q-badge">Câu {{ current_index }}</span>
                        <span class="flag">⚐</span>
                    </div>

                    <h2>{{ question.prompt }}</h2>

                    <audio class="audio-player" controls controlsList="nodownload" src="{{ audio_url }}"></audio>

                    <div class="answer-grid">
                        <button type="button" class="answer-btn" data-answer="A">
                            <b>A</b><span>{{ question.option_a }}</span>
                        </button>
                        <button type="button" class="answer-btn" data-answer="B">
                            <b>B</b><span>{{ question.option_b }}</span>
                        </button>
                        <button type="button" class="answer-btn" data-answer="C">
                            <b>C</b><span>{{ question.option_c }}</span>
                        </button>
                    </div>

                    <button class="primary-btn full check-answer" type="button">Kiểm tra đáp án</button>

                    <div class="answer-result" hidden>
                        <h3>Kết quả</h3>
                        <p>Đáp án đúng: <strong>{{ question.correct_answer }}</strong></p>
                        <div class="transcript">
                            <strong>Transcript:</strong>
                            <p>{{ question.transcript }}</p>
                        </div>
                    </div>

                    <div class="question-nav">
                        {% if prev_url %}
                            <a class="ghost-btn" href="{{ prev_url }}">← Câu trước</a>
                        {% endif %}
                        {% if next_url %}
                            <a class="primary-btn" href="{{ next_url }}">Câu tiếp theo →</a>
                        {% endif %}
                    </div>
                </article>
            {% endif %}
        </section>

        <aside class="question-side">
            <div class="side-card">
                <h3>Danh sách câu hỏi</h3>
                <div class="side-stats">
                    <div>
                        <strong>{{ current_index|default:0 }}</strong>
                        <span>Đang làm</span>
                    </div>
                    <div>
                        <strong>{{ total_questions|default:0 }}</strong>
                        <span>Tổng câu</span>
                    </div>
                </div>

                <div class="question-numbers">
                    {% for n in all_question_numbers %}
                        <a class="{% if n == current_index %}current{% endif %}" href="{% url 'listening' %}?part={{ part_number }}&q={{ n }}">{{ n }}</a>
                    {% endfor %}
                </div>

                {% if next_url %}
                    <a class="primary-btn full" href="{{ next_url }}">Đi tới câu tiếp theo</a>
                {% endif %}
            </div>
        </aside>
    </main>
</div>

<script>
document.querySelectorAll(".answer-btn").forEach(function(btn) {
    btn.addEventListener("click", function() {
        document.querySelectorAll(".answer-btn").forEach(function(x) { x.classList.remove("selected"); });
        btn.classList.add("selected");
    });
});

const checkBtn = document.querySelector(".check-answer");
if (checkBtn) {
    checkBtn.addEventListener("click", function() {
        const box = document.querySelector(".answer-result");
        if (box) box.hidden = false;
    });
}
</script>
</body>
</html>
''', encoding="utf-8")


# =========================
# 5) CSS tone đỏ
# =========================
css_dir = Path("static/core/css")
css_dir.mkdir(parents=True, exist_ok=True)
(css_dir / "app_red.css").write_text(r''':root {
    --red: #c90016;
    --red-dark: #600006;
    --red-soft: #fff0f1;
    --red-line: #ffd0d5;
    --text: #171717;
    --muted: #667085;
    --white: #ffffff;
    --shadow: 0 18px 45px rgba(96, 0, 6, .10);
}

* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--text);
    background: #fff7f8;
}

a { color: inherit; text-decoration: none; }

.admin-shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 290px 1fr;
}

.admin-sidebar {
    background: linear-gradient(180deg, #4a0005, #88000d);
    color: white;
    padding: 22px;
}

.brand-block, .brand-inline {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    width: 46px;
    height: 46px;
    display: grid;
    place-items: center;
    border-radius: 16px;
    background: var(--red);
    color: white;
    font-weight: 1000;
    box-shadow: 0 10px 22px rgba(0,0,0,.18);
}

.brand-name { font-weight: 1000; font-size: 20px; }
.brand-sub { opacity: .85; font-size: 14px; }

.side-nav {
    margin-top: 30px;
    display: grid;
    gap: 10px;
}

.side-nav a {
    padding: 14px 15px;
    border-radius: 16px;
    font-weight: 850;
    color: white;
    background: rgba(255,255,255,.08);
}

.side-nav a.active,
.side-nav a:hover {
    background: var(--red);
}

.admin-main {
    padding: 28px;
}

.admin-header {
    background: var(--white);
    border: 1px solid var(--red-line);
    border-radius: 28px;
    padding: 26px;
    box-shadow: var(--shadow);
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: center;
}

.eyebrow {
    margin: 0 0 8px;
    color: var(--red);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: .08em;
}

h1, h2, h3 { color: #390004; margin-top: 0; }

.muted { color: var(--muted); }

.primary-btn, .ghost-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 15px;
    padding: 12px 18px;
    font-weight: 900;
}

.primary-btn {
    background: var(--red);
    color: white;
}

.ghost-btn {
    background: var(--red-soft);
    color: var(--red-dark);
    border: 1px solid var(--red-line);
}

.full { width: 100%; }

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin: 22px 0;
}

.stat-card, .content-card, .question-card, .side-card, .exam-panel {
    background: white;
    border: 1px solid var(--red-line);
    border-radius: 26px;
    box-shadow: var(--shadow);
}

.stat-card {
    padding: 22px;
}

.stat-card span {
    font-size: 34px;
}

.stat-card strong {
    display: block;
    font-size: 21px;
    margin: 12px 0 8px;
    color: var(--red-dark);
}

.stat-card a {
    color: var(--red);
    font-weight: 900;
}

.content-card {
    padding: 24px;
}

.section-head {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: center;
    margin-bottom: 16px;
}

.lesson-list {
    display: grid;
    gap: 12px;
}

.lesson-item, .empty-box {
    border: 1px solid #f3d4d7;
    background: #fffafa;
    border-radius: 18px;
    padding: 18px;
}

.student-body {
    background: linear-gradient(135deg, #fff8f8, #ffe8ea);
}

.student-shell {
    min-height: 100vh;
    padding: 22px;
}

.student-top {
    max-width: 1220px;
    margin: 0 auto 22px;
    background: white;
    border: 1px solid var(--red-line);
    border-radius: 24px;
    box-shadow: var(--shadow);
    padding: 16px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-inline span {
    display: block;
    color: var(--muted);
    font-size: 13px;
}

.student-actions {
    display: flex;
    gap: 10px;
}

.student-layout {
    max-width: 1220px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 310px;
    gap: 22px;
    align-items: start;
}

.exam-panel {
    padding: 24px;
}

.exam-title {
    display: flex;
    gap: 16px;
    align-items: center;
}

.part-card {
    width: 92px;
    height: 92px;
    border-radius: 24px;
    background: var(--red);
    color: white;
    display: grid;
    place-items: center;
    text-align: center;
    box-shadow: 0 18px 35px rgba(201,0,22,.24);
}

.part-card span { font-size: 13px; text-transform: uppercase; letter-spacing: .1em; }
.part-card strong { font-size: 34px; }

.part-tabs {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 24px 0;
}

.part-tabs a {
    padding: 10px 16px;
    border-radius: 999px;
    background: var(--red-soft);
    color: var(--red-dark);
    border: 1px solid var(--red-line);
    font-weight: 900;
}

.part-tabs a.active {
    background: var(--red);
    color: white;
}

.progress-wrap {
    margin-bottom: 18px;
}

.progress-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    color: var(--red-dark);
}

.progress-bar {
    height: 10px;
    border-radius: 999px;
    background: #ffe0e3;
    overflow: hidden;
}

.progress-bar div {
    height: 100%;
    background: var(--red);
}

.question-card {
    padding: 24px;
}

.question-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.q-badge, .flag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: var(--red-soft);
    color: var(--red-dark);
    border: 1px solid var(--red-line);
    font-weight: 900;
    padding: 8px 12px;
}

.audio-player {
    width: 100%;
    margin: 18px 0;
}

.answer-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0,1fr));
    gap: 12px;
}

.answer-btn {
    border: 1px solid var(--red-line);
    border-radius: 18px;
    background: white;
    padding: 15px;
    text-align: left;
    display: flex;
    gap: 12px;
    align-items: center;
    cursor: pointer;
}

.answer-btn b {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--red-soft);
    color: var(--red-dark);
    display: grid;
    place-items: center;
}

.answer-btn.selected {
    border-color: var(--red);
    background: #fff1f2;
    box-shadow: 0 0 0 4px rgba(201,0,22,.08);
}

.check-answer {
    margin-top: 16px;
}

.answer-result {
    margin-top: 16px;
    border-radius: 18px;
    background: #fff6f6;
    border: 1px solid var(--red-line);
    padding: 16px;
}

.question-nav {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    gap: 12px;
}

.question-side {
    position: sticky;
    top: 18px;
}

.side-card {
    padding: 20px;
}

.side-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 16px 0;
}

.side-stats div {
    background: var(--red-soft);
    border: 1px solid var(--red-line);
    border-radius: 16px;
    padding: 14px;
}

.side-stats strong {
    display: block;
    font-size: 28px;
    color: var(--red-dark);
}

.side-stats span {
    font-size: 13px;
    color: var(--muted);
}

.question-numbers {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-bottom: 16px;
}

.question-numbers a {
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    border: 1px solid var(--red-line);
    background: white;
    font-weight: 900;
}

.question-numbers a.current {
    background: var(--red);
    color: white;
}

@media (max-width: 900px) {
    .admin-shell { grid-template-columns: 1fr; }
    .admin-sidebar { position: relative; }
    .stat-grid { grid-template-columns: 1fr; }
    .student-layout { grid-template-columns: 1fr; }
    .question-side { position: static; }
    .answer-grid { grid-template-columns: 1fr; }
    .student-top, .admin-header, .section-head { flex-direction: column; align-items: stretch; }
}
''', encoding="utf-8")

print("DA_TAO_GIAO_DIEN_ADMIN_VA_HOC_VIEN_TONE_DO")
