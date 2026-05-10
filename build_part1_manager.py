from pathlib import Path
import re

# =========================
# 1) Thêm view quản lý Part 1 custom
# =========================
views_path = Path("core/views.py")
views = views_path.read_text(encoding="utf-8", errors="ignore")

if "def admin_part1_questions" not in views:
    insert = r'''

@login_required
def admin_part1_questions(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.username == "admin"):
        return redirect("listening")

    edit_id = request.GET.get("edit")
    editing_question = None

    if edit_id:
        editing_question = ListeningQuestion.objects.filter(id=edit_id, part=1).first()

    if request.method == "POST":
        question_id = request.POST.get("question_id", "").strip()

        if question_id:
            question = get_object_or_404(ListeningQuestion, id=question_id, part=1)
        else:
            question = ListeningQuestion(part=1)

        question.question_number = int(request.POST.get("question_number") or 1)
        question.question_text = request.POST.get("question_text", "").strip()
        question.audio_drive_link = request.POST.get("audio_drive_link", "").strip()
        question.audio_url = request.POST.get("audio_url", "").strip()
        question.option_a = request.POST.get("option_a", "").strip()
        question.option_b = request.POST.get("option_b", "").strip()
        question.option_c = request.POST.get("option_c", "").strip()
        question.correct_answer = request.POST.get("correct_answer", "A").strip().upper()[:1] or "A"
        question.listening_transcript = request.POST.get("listening_transcript", "").strip()
        question.save()

        messages.success(request, "Đã lưu câu hỏi Part 1 thành công.")
        return redirect("admin_part1_questions")

    delete_id = request.GET.get("delete")
    if delete_id:
        ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
        messages.success(request, "Đã xóa câu hỏi Part 1.")
        return redirect("admin_part1_questions")

    questions = ListeningQuestion.objects.filter(part=1).order_by("question_number", "id")

    return render(request, "core/admin_part1_questions.html", {
        "questions": questions,
        "editing_question": editing_question,
    })
'''
    views += insert
    views_path.write_text(views, encoding="utf-8")
    print("DA_THEM_VIEW_ADMIN_PART1")
else:
    print("VIEW_ADMIN_PART1_DA_CO")


# =========================
# 2) Thêm URL /dashboard/part-1/
# =========================
urls_path = Path("core/urls.py")
urls = urls_path.read_text(encoding="utf-8", errors="ignore")

if 'name="admin_part1_questions"' not in urls:
    marker = 'path("dashboard/", views.dashboard, name="dashboard"),'
    replacement = marker + ' path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
    urls = urls.replace(marker, replacement)
    urls_path.write_text(urls, encoding="utf-8")
    print("DA_THEM_URL_ADMIN_PART1")
else:
    print("URL_ADMIN_PART1_DA_CO")


# =========================
# 3) Sửa dashboard menu: Quản lý câu hỏi Listening đi tới trang custom
# =========================
dash_path = Path("templates/core/dashboard.html")
dash = dash_path.read_text(encoding="utf-8", errors="ignore")

dash = dash.replace('data-src="/admin/core/listeningquestion/"', 'data-src="" data-href="{% url \'admin_part1_questions\' %}"')
dash = dash.replace('<button class="side-link" data-title="Quản lý câu hỏi Listening" data-src="">', '<a class="side-link" href="{% url \'admin_part1_questions\' %}">')
dash = dash.replace('</button>\n\n        <button class="side-link" data-title="Duyệt học viên"', '</a>\n\n        <button class="side-link" data-title="Duyệt học viên"', 1)

dash = dash.replace('data-title="Quản lý câu hỏi Listening" data-src="/admin/core/listeningquestion/"', 'onclick="window.location.href=\'{% url \\'admin_part1_questions\\' %}\'"')

dash_path.write_text(dash, encoding="utf-8")
print("DA_SUA_MENU_DASHBOARD")


# =========================
# 4) Tạo template quản lý Part 1 đẹp
# =========================
Path("templates/core/admin_part1_questions.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Quản lý Part 1 | Điểm TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/admin_panel.css' %}">
    <link rel="stylesheet" href="{% static 'core/css/admin_part1.css' %}">
</head>
<body class="admin-page">
<div class="admin-shell">
    <aside class="admin-sidebar">
        <div class="brand">
            <div class="brand-logo">A</div>
            <div>
                <strong>Điểm TSA</strong>
                <span>với Aptis</span>
            </div>
        </div>

        <a class="side-link" href="{% url 'dashboard' %}">🎧 Tổng quan Admin</a>
        <a class="side-link active" href="{% url 'admin_part1_questions' %}">🎧 Quản lý Part 1</a>
        <a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt học viên</a>
        <a class="side-link" href="/admin/core/lesson/">📚 Quản lý bài học</a>
        <a class="side-link" href="/admin/core/securityalert/">🛡️ Cảnh báo bảo mật</a>
        <a class="side-link" href="{% url 'listening' %}">👀 Xem giao diện học viên</a>
        <a class="side-link logout" href="{% url 'logout' %}">🚪 Đăng xuất</a>
    </aside>

    <main class="admin-main">
        <header class="admin-header part1-header">
            <div>
                <p class="eyebrow">Listening Question Bank</p>
                <h1>Quản lý câu hỏi Part 1</h1>
                <p class="muted">Thêm, sửa, xóa câu hỏi Part 1 ngay trong dashboard. Không cần nhảy sang giao diện Django Admin.</p>
            </div>
            <a class="primary-btn" href="{% url 'dashboard' %}">← Về tổng quan</a>
        </header>

        {% if messages %}
            <div class="message-stack">
                {% for message in messages %}
                    <div class="toast {{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}

        <section class="part1-grid">
            <form method="post" class="question-form">
                {% csrf_token %}
                <input type="hidden" name="question_id" value="{% if editing_question %}{{ editing_question.id }}{% endif %}">

                <div class="form-head">
                    <div>
                        <h2>{% if editing_question %}Sửa câu hỏi{% else %}Thêm câu hỏi mới{% endif %}</h2>
                        <p>Điền câu hỏi, audio, 3 đáp án và đáp án đúng.</p>
                    </div>
                    {% if editing_question %}
                        <a class="ghost-btn" href="{% url 'admin_part1_questions' %}">Hủy sửa</a>
                    {% endif %}
                </div>

                <div class="field-row two">
                    <label>
                        <span>Số câu</span>
                        <input type="number" name="question_number" min="1" value="{% if editing_question %}{{ editing_question.question_number }}{% else %}{{ questions.count|add:1 }}{% endif %}" required>
                    </label>

                    <label>
                        <span>Đáp án đúng</span>
                        <select name="correct_answer">
                            <option value="A" {% if editing_question.correct_answer == "A" %}selected{% endif %}>A</option>
                            <option value="B" {% if editing_question.correct_answer == "B" %}selected{% endif %}>B</option>
                            <option value="C" {% if editing_question.correct_answer == "C" %}selected{% endif %}>C</option>
                        </select>
                    </label>
                </div>

                <label>
                    <span>Câu hỏi</span>
                    <textarea name="question_text" rows="3" required>{% if editing_question %}{{ editing_question.question_text }}{% endif %}</textarea>
                </label>

                <label>
                    <span>Link Google Drive MP3</span>
                    <input type="url" name="audio_drive_link" value="{% if editing_question %}{{ editing_question.audio_drive_link }}{% endif %}" placeholder="Dán link audio Google Drive nếu có">
                </label>

                <label>
                    <span>Link audio ngoài</span>
                    <input type="url" name="audio_url" value="{% if editing_question %}{{ editing_question.audio_url }}{% endif %}" placeholder="Hoặc dán link audio trực tiếp">
                </label>

                <div class="field-row three">
                    <label>
                        <span>Đáp án A</span>
                        <input type="text" name="option_a" value="{% if editing_question %}{{ editing_question.option_a }}{% endif %}" required>
                    </label>
                    <label>
                        <span>Đáp án B</span>
                        <input type="text" name="option_b" value="{% if editing_question %}{{ editing_question.option_b }}{% endif %}" required>
                    </label>
                    <label>
                        <span>Đáp án C</span>
                        <input type="text" name="option_c" value="{% if editing_question %}{{ editing_question.option_c }}{% endif %}" required>
                    </label>
                </div>

                <label>
                    <span>Transcript / lời thoại</span>
                    <textarea name="listening_transcript" rows="5">{% if editing_question %}{{ editing_question.listening_transcript }}{% endif %}</textarea>
                </label>

                <button class="primary-btn full" type="submit">
                    {% if editing_question %}Lưu thay đổi{% else %}+ Thêm câu hỏi Part 1{% endif %}
                </button>
            </form>

            <aside class="part1-summary">
                <div class="summary-card">
                    <span>Tổng câu</span>
                    <strong>{{ questions.count }}</strong>
                    <p>Part 1 hiện có {{ questions.count }} câu hỏi.</p>
                </div>
                <div class="summary-card soft">
                    <span>Gợi ý</span>
                    <p>Sắp xếp số câu theo thứ tự 1, 2, 3... để học viên làm bài đúng luồng.</p>
                </div>
            </aside>
        </section>

        <section class="question-list-card">
            <div class="section-head">
                <div>
                    <h2>Danh sách câu hỏi Part 1</h2>
                    <p>Các câu sẽ hiển thị bên giao diện học viên theo thứ tự số câu.</p>
                </div>
            </div>

            <div class="question-table-wrap">
                <table class="question-table">
                    <thead>
                    <tr>
                        <th>Câu</th>
                        <th>Nội dung</th>
                        <th>Audio</th>
                        <th>A</th>
                        <th>B</th>
                        <th>C</th>
                        <th>Đúng</th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                    {% for q in questions %}
                        <tr>
                            <td><strong>{{ q.question_number }}</strong></td>
                            <td class="question-text">{{ q.question_text }}</td>
                            <td>
                                {% if q.audio_drive_link %}
                                    <span class="audio-pill">Drive</span>
                                {% elif q.audio_url %}
                                    <span class="audio-pill">URL</span>
                                {% elif q.audio_file %}
                                    <span class="audio-pill">File</span>
                                {% else %}
                                    <span class="missing-pill">Chưa có</span>
                                {% endif %}
                            </td>
                            <td>{{ q.option_a }}</td>
                            <td>{{ q.option_b }}</td>
                            <td>{{ q.option_c }}</td>
                            <td><span class="answer-pill">{{ q.correct_answer }}</span></td>
                            <td class="action-cell">
                                <a class="mini-btn" href="?edit={{ q.id }}">Sửa</a>
                                <a class="mini-btn danger" href="?delete={{ q.id }}" onclick="return confirm('Xóa câu hỏi này?')">Xóa</a>
                            </td>
                        </tr>
                    {% empty %}
                        <tr>
                            <td colspan="8">
                                <div class="empty-box">Chưa có câu hỏi Part 1 nào. Thêm câu đầu tiên ở form phía trên.</div>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </section>
    </main>
</div>
</body>
</html>
''', encoding="utf-8")


# =========================
# 5) CSS Part 1
# =========================
Path("static/core/css/admin_part1.css").write_text(r'''.part1-header h1 {
    font-size: clamp(34px, 5vw, 54px);
}

.message-stack {
    margin-bottom: 18px;
}

.toast {
    background: #fff5f5;
    border: 1px solid #ffc9d0;
    color: #65000a;
    border-radius: 16px;
    padding: 14px 18px;
    font-weight: 800;
}

.part1-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 280px;
    gap: 22px;
    align-items: start;
    margin-bottom: 24px;
}

.question-form,
.summary-card,
.question-list-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 28px;
    box-shadow: var(--shadow);
}

.question-form {
    padding: 26px;
}

.form-head {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: start;
    margin-bottom: 20px;
}

.form-head h2 {
    margin: 0 0 8px;
    font-size: 28px;
}

.form-head p {
    margin: 0;
    color: var(--muted);
}

.question-form label {
    display: grid;
    gap: 8px;
    margin-bottom: 15px;
    font-weight: 900;
    color: #520006;
}

.question-form input,
.question-form textarea,
.question-form select {
    width: 100%;
    border: 1px solid #ffc8cf;
    border-radius: 15px;
    padding: 13px 14px;
    outline: none;
    background: #fffafa;
    color: #1f2937;
    font: inherit;
}

.question-form input:focus,
.question-form textarea:focus,
.question-form select:focus {
    border-color: var(--red);
    box-shadow: 0 0 0 4px rgba(214,0,24,.08);
    background: white;
}

.field-row {
    display: grid;
    gap: 14px;
}

.field-row.two {
    grid-template-columns: 180px 180px;
}

.field-row.three {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.summary-card {
    padding: 22px;
    margin-bottom: 16px;
}

.summary-card span {
    display: block;
    color: var(--red);
    font-weight: 1000;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 10px;
}

.summary-card strong {
    display: block;
    font-size: 52px;
    color: var(--red-dark);
    line-height: 1;
}

.summary-card p {
    color: var(--muted);
    line-height: 1.5;
}

.summary-card.soft {
    background: #fff5f6;
}

.question-list-card {
    padding: 26px;
}

.question-table-wrap {
    overflow: auto;
    border: 1px solid #ffe0e4;
    border-radius: 20px;
}

.question-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1150px;
}

.question-table th,
.question-table td {
    padding: 14px 15px;
    border-bottom: 1px solid #ffe0e4;
    vertical-align: top;
    text-align: left;
}

.question-table th {
    background: #fff1f3;
    color: #65000a;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .05em;
}

.question-table tr:hover td {
    background: #fffafa;
}

.question-text {
    min-width: 260px;
    font-weight: 750;
    color: #2b0005;
}

.audio-pill,
.missing-pill,
.answer-pill {
    display: inline-flex;
    border-radius: 999px;
    padding: 6px 10px;
    font-weight: 900;
    font-size: 12px;
}

.audio-pill {
    background: #e8fff2;
    color: #08703c;
}

.missing-pill {
    background: #fff2d9;
    color: #9a5b00;
}

.answer-pill {
    background: var(--red);
    color: white;
}

.action-cell {
    white-space: nowrap;
}

.mini-btn {
    display: inline-flex;
    padding: 8px 10px;
    border-radius: 10px;
    background: #fff1f3;
    color: #6a0008;
    border: 1px solid #ffd2d8;
    font-weight: 900;
    margin-right: 6px;
}

.mini-btn.danger {
    background: #ffe7e9;
    color: #c90016;
}

@media (max-width: 1100px) {
    .part1-grid {
        grid-template-columns: 1fr;
    }

    .field-row.two,
    .field-row.three {
        grid-template-columns: 1fr;
    }
}
''', encoding="utf-8")

print("DA_THIET_KE_QUAN_LY_CAU_HOI_PART1")
