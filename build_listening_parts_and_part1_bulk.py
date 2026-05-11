from pathlib import Path
import re

# =========================
# 1) Add/sửa views manage Listening Parts + Part 1 hàng loạt
# =========================
views_path = Path("core/views.py")
views = views_path.read_text(encoding="utf-8", errors="ignore")

block = r'''

@login_required
def admin_listening_parts(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.username == "admin"):
        return redirect("listening")

    part_counts = {
        1: ListeningQuestion.objects.filter(part=1).count(),
        2: ListeningQuestion.objects.filter(part=2).count(),
        3: ListeningQuestion.objects.filter(part=3).count(),
        4: ListeningQuestion.objects.filter(part=4).count(),
    }

    return render(request, "core/admin_listening_parts.html", {
        "part_counts": part_counts,
    })


@login_required
def admin_part1_questions(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.username == "admin"):
        return redirect("listening")

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "create_blank":
            try:
                count = int(request.POST.get("create_count", 10))
            except ValueError:
                count = 10

            count = max(1, min(count, 100))

            current_max = 0
            for q in ListeningQuestion.objects.filter(part=1):
                try:
                    current_max = max(current_max, int(q.question_number or 0))
                except Exception:
                    pass

            for i in range(1, count + 1):
                ListeningQuestion.objects.create(
                    part=1,
                    question_number=current_max + i,
                    question_text=f"Question {current_max + i}",
                    option_a="",
                    option_b="",
                    option_c="",
                    correct_answer="A",
                    listening_transcript="",
                )

            messages.success(request, f"Đã tạo thêm {count} dòng Part 1.")
            return redirect("admin_part1_questions")

        if action == "save_all":
            row_ids = request.POST.getlist("row_id")

            for row_id in row_ids:
                q = ListeningQuestion.objects.filter(id=row_id, part=1).first()
                if not q:
                    continue

                try:
                    q.question_number = int(request.POST.get(f"question_number_{row_id}") or q.question_number or 1)
                except ValueError:
                    pass

                q.question_text = request.POST.get(f"question_text_{row_id}", "").strip()
                q.option_a = request.POST.get(f"option_a_{row_id}", "").strip()
                q.option_b = request.POST.get(f"option_b_{row_id}", "").strip()
                q.option_c = request.POST.get(f"option_c_{row_id}", "").strip()
                q.correct_answer = request.POST.get(f"correct_answer_{row_id}", "A").strip().upper()[:1] or "A"
                q.listening_transcript = request.POST.get(f"listening_transcript_{row_id}", "").strip()

                audio_drive_link = request.POST.get(f"audio_drive_link_{row_id}", "").strip()
                if hasattr(q, "audio_drive_link"):
                    q.audio_drive_link = audio_drive_link

                audio_url = request.POST.get(f"audio_url_{row_id}", "").strip()
                if hasattr(q, "audio_url"):
                    q.audio_url = audio_url

                q.save()

            messages.success(request, "Đã cập nhật hàng loạt questions Part 1.")
            return redirect("admin_part1_questions")

        if action == "delete_one":
            delete_id = request.POST.get("delete_id")
            ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
            messages.success(request, "Đã xóa 1 questions Part 1.")
            return redirect("admin_part1_questions")

    questions = ListeningQuestion.objects.filter(part=1).order_by("question_number", "id")

    return render(request, "core/admin_part1_questions.html", {
        "questions": questions,
        "total_questions": questions.count(),
    })
'''

views = re.sub(
    r'\n@login_required\s+def admin_listening_parts\(request\):.*?(?=\n@login_required\s+def|\Z)',
    "\n",
    views,
    flags=re.S
)

views = re.sub(
    r'\n@login_required\s+def admin_part1_questions\(request\):.*?(?=\n@login_required\s+def|\Z)',
    "\n",
    views,
    flags=re.S
)

views = views.rstrip() + block + "\n"
views_path.write_text(views, encoding="utf-8")
print("DA_CAP_NHAT_VIEWS_PARTS_PART1")


# =========================
# 2) Add URL
# =========================
urls_path = Path("core/urls.py")
urls = urls_path.read_text(encoding="utf-8", errors="ignore")

if 'name="admin_listening_parts"' not in urls:
    urls = urls.replace(
        'path("dashboard/", views.dashboard, name="dashboard"),',
        'path("dashboard/", views.dashboard, name="dashboard"),\n    path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),\n    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
    )

if 'name="admin_part1_questions"' not in urls:
    urls = urls.replace(
        'path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),',
        'path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),\n    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
    )

urls_path.write_text(urls, encoding="utf-8")
print("DA_CAP_NHAT_URLS")


# =========================
# 3) Edit dashboard: menu Listening đi tới màn 4 Part
# =========================
dash_path = Path("templates/core/dashboard.html")
if dash_path.exists():
    dash = dash_path.read_text(encoding="utf-8", errors="ignore")

    dash = dash.replace('/admin/core/listeningquestion/', '{% url "admin_listening_parts" %}')
    dash = dash.replace('{% url \\'admin_part1_questions\\' %}', '{% url "admin_listening_parts" %}')
    dash = dash.replace("{% url 'admin_part1_questions' %}", '{% url "admin_listening_parts" %}')

    # Nếu trong dashboard đang dùng button iframe cũ, đổi separate nút Listening thành link thật.
    dash = dash.replace(
        '<button class="side-link" data-title="Manage questions Listening" data-src="{% url "admin_listening_parts" %}">',
        '<a class="side-link" href="{% url "admin_listening_parts" %}">'
    )
    dash = dash.replace(
        '<button class="side-link" data-title="Manage questions Listening" data-src="">',
        '<a class="side-link" href="{% url "admin_listening_parts" %}">'
    )
    dash = dash.replace(
        '</button>\n\n        <button class="side-link" data-title="Duyệt student"',
        '</a>\n\n        <button class="side-link" data-title="Duyệt student"',
        1
    )

    dash_path.write_text(dash, encoding="utf-8")
    print("DA_CAP_NHAT_MENU_DASHBOARD")


# =========================
# 4) Template màn 4 Part
# =========================
Path("templates/core/admin_listening_parts.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Manage Listening | Score TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/admin_panel.css' %}">
    <link rel="stylesheet" href="{% static 'core/css/admin_listening_parts.css' %}">
</head>
<body class="admin-page">
<div class="admin-shell">
    <aside class="admin-sidebar">
        <div class="brand">
            <div class="brand-logo">A</div>
            <div>
                <strong>Score TSA</strong>
                <span>với Aptis</span>
            </div>
        </div>

        <a class="side-link" href="{% url 'dashboard' %}">🎧 Admin Overview</a>
        <a class="side-link active" href="{% url 'admin_listening_parts' %}">🎧 Manage questions Listening</a>
        <a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt student</a>
        <a class="side-link" href="/admin/core/lesson/">📚 Manage lesson</a>
        <a class="side-link" href="/admin/core/securityalert/">🛡️ Security Alerts</a>
        <a class="side-link" href="{% url 'listening' %}">👀 View Student Interface</a>
        <a class="side-link logout" href="{% url 'logout' %}">🚪 Logout</a>
    </aside>

    <main class="admin-main">
        <header class="admin-header">
            <div>
                <p class="eyebrow">Listening Bank</p>
                <h1>Manage questions Listening</h1>
                <p class="muted">Chọn từng Part để khai thác sâu. Bây giờ ưu tiên hoàn thiện Part 1 trước.</p>
            </div>
            <a class="primary-btn" href="{% url 'dashboard' %}">← Về tổng quan</a>
        </header>

        <section class="parts-grid">
            <a class="part-card active" href="{% url 'admin_part1_questions' %}">
                <div class="part-icon">1</div>
                <div>
                    <h2>Part 1</h2>
                    <p>Update hàng loạt questions, audio, answer và transcript.</p>
                    <strong>{{ part_counts.1 }} questions</strong>
                </div>
            </a>

            <div class="part-card locked">
                <div class="part-icon">2</div>
                <div>
                    <h2>Part 2</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện luồng Part 1.</p>
                    <strong>{{ part_counts.2 }} questions</strong>
                </div>
            </div>

            <div class="part-card locked">
                <div class="part-icon">3</div>
                <div>
                    <h2>Part 3</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện luồng Part 1.</p>
                    <strong>{{ part_counts.3 }} questions</strong>
                </div>
            </div>

            <div class="part-card locked">
                <div class="part-icon">4</div>
                <div>
                    <h2>Part 4</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện luồng Part 1.</p>
                    <strong>{{ part_counts.4 }} questions</strong>
                </div>
            </div>
        </section>
    </main>
</div>
</body>
</html>
''', encoding="utf-8")


# =========================
# 5) Template bảng hàng loạt Part 1
# =========================
Path("templates/core/admin_part1_questions.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Part 1 | Manage hàng loạt</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/admin_panel.css' %}">
    <link rel="stylesheet" href="{% static 'core/css/admin_listening_parts.css' %}">
</head>
<body class="admin-page">
<div class="admin-shell">
    <aside class="admin-sidebar">
        <div class="brand">
            <div class="brand-logo">A</div>
            <div>
                <strong>Score TSA</strong>
                <span>với Aptis</span>
            </div>
        </div>

        <a class="side-link" href="{% url 'dashboard' %}">🎧 Admin Overview</a>
        <a class="side-link active" href="{% url 'admin_listening_parts' %}">🎧 Manage questions Listening</a>
        <a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt student</a>
        <a class="side-link" href="/admin/core/lesson/">📚 Manage lesson</a>
        <a class="side-link" href="/admin/core/securityalert/">🛡️ Security Alerts</a>
        <a class="side-link" href="{% url 'listening' %}">👀 View Student Interface</a>
        <a class="side-link logout" href="{% url 'logout' %}">🚪 Logout</a>
    </aside>

    <main class="admin-main">
        <header class="admin-header">
            <div>
                <p class="eyebrow">Part 1 Manager</p>
                <h1>Manage Part 1 Questions</h1>
                <p class="muted">Bulk Update Table data. Save một lần cho toàn bộ questions.</p>
            </div>
            <a class="primary-btn" href="{% url 'admin_listening_parts' %}">← Choose Part khác</a>
        </header>

        {% if messages %}
            <div class="message-stack">
                {% for message in messages %}
                    <div class="toast {{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}

        <section class="toolbar-card">
            <div>
                <h2>Part 1 hiện có {{ total_questions }} questions</h2>
                <p>Nếu bạn đã upload audio trước đó, bảng dưới sẽ giữ link/file audio hiện có và cho bạn nhập thêm questions, answer, transcript.</p>
            </div>

            <form method="post" class="create-row-form">
                {% csrf_token %}
                <input type="hidden" name="action" value="create_blank">
                <input type="number" name="create_count" min="1" max="100" value="13">
                <button class="ghost-btn" type="submit">+ Tạo thêm dòng</button>
            </form>
        </section>

        <form method="post" class="bulk-card">
            {% csrf_token %}
            <input type="hidden" name="action" value="save_all">

            <div class="bulk-head">
                <div>
                    <h2>Bulk Update Table</h2>
                    <p>Edit trực tiếp trong bảng rồi bấm “Save toàn bộ Part 1”.</p>
                </div>
                <button class="primary-btn" type="submit">💾 Save All Part 1</button>
            </div>

            <div class="bulk-table-wrap">
                <table class="bulk-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Question</th>
                            <th>Audio Drive</th>
                            <th>Audio URL</th>
                            <th>Answer A</th>
                            <th>Answer B</th>
                            <th>Answer C</th>
                            <th>Đúng</th>
                            <th>Transcript</th>
                            <th>Delete</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for q in questions %}
                        <tr>
                            <td>
                                <input type="hidden" name="row_id" value="{{ q.id }}">
                                <input class="short-input" type="number" name="question_number_{{ q.id }}" value="{{ q.question_number }}">
                            </td>
                            <td>
                                <textarea name="question_text_{{ q.id }}" rows="3">{{ q.question_text }}</textarea>
                            </td>
                            <td>
                                <textarea name="audio_drive_link_{{ q.id }}" rows="3">{% if q.audio_drive_link %}{{ q.audio_drive_link }}{% endif %}</textarea>
                            </td>
                            <td>
                                <textarea name="audio_url_{{ q.id }}" rows="3">{% if q.audio_url %}{{ q.audio_url }}{% endif %}</textarea>
                            </td>
                            <td><textarea name="option_a_{{ q.id }}" rows="2">{{ q.option_a }}</textarea></td>
                            <td><textarea name="option_b_{{ q.id }}" rows="2">{{ q.option_b }}</textarea></td>
                            <td><textarea name="option_c_{{ q.id }}" rows="2">{{ q.option_c }}</textarea></td>
                            <td>
                                <select name="correct_answer_{{ q.id }}">
                                    <option value="A" {% if q.correct_answer == "A" %}selected{% endif %}>A</option>
                                    <option value="B" {% if q.correct_answer == "B" %}selected{% endif %}>B</option>
                                    <option value="C" {% if q.correct_answer == "C" %}selected{% endif %}>C</option>
                                </select>
                            </td>
                            <td>
                                <textarea name="listening_transcript_{{ q.id }}" rows="3">{{ q.listening_transcript }}</textarea>
                            </td>
                            <td>
                                <button class="delete-btn" type="submit" name="delete_id" value="{{ q.id }}" formaction="" onclick="this.form.action.value='delete_one'; return confirm('Delete câu này?')">Delete</button>
                            </td>
                        </tr>
                    {% empty %}
                        <tr>
                            <td colspan="10">
                                <div class="empty-box">Chưa có dòng nào. Hãy tạo thêm dòng ở phía trên.</div>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="sticky-save">
                <button class="primary-btn" type="submit">💾 Save All Part 1</button>
            </div>
        </form>
    </main>
</div>

<script>
document.querySelectorAll(".delete-btn").forEach(function(btn) {
    btn.addEventListener("click", function() {
        const form = btn.closest("form");
        const actionInput = form.querySelector("input[name='action']");
        if (actionInput) actionInput.value = "delete_one";
    });
});
</script>
</body>
</html>
''', encoding="utf-8")


# =========================
# 6) CSS cho 4 Part + bảng Part 1
# =========================
Path("static/core/css/admin_listening_parts.css").write_text(r'''.parts-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
}

.part-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 28px;
    padding: 24px;
    box-shadow: var(--shadow);
    display: grid;
    gap: 18px;
    min-height: 245px;
}

.part-card.active {
    cursor: pointer;
}

.part-card.active:hover {
    transform: translateY(-3px);
    border-color: #ff9aa5;
}

.part-card.locked {
    opacity: .72;
}

.part-icon {
    width: 68px;
    height: 68px;
    border-radius: 22px;
    background: var(--red);
    color: white;
    display: grid;
    place-items: center;
    font-size: 34px;
    font-weight: 1000;
    box-shadow: 0 16px 30px rgba(214,0,24,.22);
}

.part-card h2 {
    font-size: 28px;
    margin: 0 0 10px;
}

.part-card p {
    color: var(--muted);
    line-height: 1.55;
}

.part-card strong {
    color: var(--red-dark);
    font-size: 18px;
}

.message-stack {
    margin-bottom: 18px;
}

.toast {
    padding: 14px 18px;
    border-radius: 18px;
    background: #fff3f4;
    border: 1px solid #ffcfd5;
    color: #670006;
    font-weight: 850;
}

.toolbar-card,
.bulk-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 28px;
    box-shadow: var(--shadow);
}

.toolbar-card {
    padding: 22px;
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: center;
    margin-bottom: 22px;
}

.toolbar-card h2 {
    margin: 0 0 8px;
}

.toolbar-card p {
    margin: 0;
    color: var(--muted);
}

.create-row-form {
    display: flex;
    gap: 10px;
    align-items: center;
}

.create-row-form input {
    width: 90px;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 12px;
    font-weight: 900;
}

.bulk-card {
    padding: 22px;
}

.bulk-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}

.bulk-head h2 {
    margin: 0 0 8px;
}

.bulk-head p {
    margin: 0;
    color: var(--muted);
}

.bulk-table-wrap {
    overflow: auto;
    border: 1px solid #ffe0e4;
    border-radius: 20px;
    max-height: calc(100vh - 290px);
}

.bulk-table {
    width: 100%;
    min-width: 1600px;
    border-collapse: collapse;
}

.bulk-table th,
.bulk-table td {
    border-bottom: 1px solid #ffe0e4;
    border-right: 1px solid #fff0f2;
    padding: 10px;
    vertical-align: top;
}

.bulk-table th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: #fff1f3;
    color: #640008;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: .04em;
}

.bulk-table input,
.bulk-table textarea,
.bulk-table select {
    width: 100%;
    border: 1px solid #ffd0d6;
    border-radius: 12px;
    padding: 9px 10px;
    background: #fffafa;
    font: inherit;
    outline: none;
}

.bulk-table textarea {
    resize: vertical;
    min-height: 58px;
}

.bulk-table input:focus,
.bulk-table textarea:focus,
.bulk-table select:focus {
    border-color: var(--red);
    box-shadow: 0 0 0 3px rgba(214,0,24,.08);
    background: white;
}

.short-input {
    max-width: 75px;
    font-weight: 900;
    text-align: center;
}

.delete-btn {
    border: 1px solid #ffcfd5;
    background: #fff1f3;
    color: #c90016;
    border-radius: 12px;
    padding: 9px 12px;
    font-weight: 900;
    cursor: pointer;
}

.sticky-save {
    position: sticky;
    bottom: 0;
    background: linear-gradient(180deg, rgba(255,255,255,.4), #fff);
    padding-top: 16px;
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
}

@media (max-width: 1200px) {
    .parts-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .toolbar-card,
    .bulk-head {
        flex-direction: column;
        align-items: stretch;
    }
}

@media (max-width: 760px) {
    .parts-grid {
        grid-template-columns: 1fr;
    }
}
''', encoding="utf-8")

print("DA_TAO_4_PART_VA_BANG_HANG_LOAT_PART1")
