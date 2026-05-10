from pathlib import Path
import re

# 1) Đảm bảo URL có trang chọn 4 Part và Part 1
urls_path = Path("core/urls.py")
urls = urls_path.read_text(encoding="utf-8", errors="ignore")

if 'admin_listening_parts' not in urls:
    urls = urls.replace(
        'path("dashboard/", views.dashboard, name="dashboard"),',
        'path("dashboard/", views.dashboard, name="dashboard"),\n    path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),\n    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
    )
elif 'admin_part1_questions' not in urls:
    urls = urls.replace(
        'path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),',
        'path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),\n    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
    )

urls_path.write_text(urls, encoding="utf-8")


# 2) Sửa dashboard: bỏ iframe lỗi, menu Listening thành link thật
dash_path = Path("templates/core/dashboard.html")
dash = dash_path.read_text(encoding="utf-8", errors="ignore")

dash = re.sub(
    r'<button class="side-link active"[^>]*>\s*🎧\s*Tổng quan Admin\s*</button>',
    '<a class="side-link active" href="{% url \'dashboard\' %}">🎧 Tổng quan Admin</a>',
    dash,
    flags=re.S
)

dash = re.sub(
    r'<button class="side-link"[^>]*>\s*🎧\s*Quản lý câu hỏi\s*Listening\s*</button>',
    '<a class="side-link" href="{% url \'admin_listening_parts\' %}">🎧 Quản lý câu hỏi Listening</a>',
    dash,
    flags=re.S
)

dash = re.sub(
    r'<button class="quick-card"[^>]*>\s*<span>🎧</span>\s*<strong>Listening</strong>(.*?)</button>',
    '<a class="quick-card" href="{% url \'admin_listening_parts\' %}"><span>🎧</span><strong>Listening</strong>\\1</a>',
    dash,
    flags=re.S
)

# Nếu còn iframe panel cũ thì ẩn hẳn để không hiện khung xám lỗi
dash = re.sub(
    r'<section id="framePanel".*?</section>',
    '',
    dash,
    flags=re.S
)

# Nếu còn JS iframe cũ thì xóa
dash = re.sub(
    r'<script>\s*\(function \(\).*?</script>',
    '',
    dash,
    flags=re.S
)

dash_path.write_text(dash, encoding="utf-8")
print("DA_SUA_MENU_LISTENING_KHONG_IFRAME")


# 3) Tạo lại trang 4 Part nếu thiếu
Path("templates/core/admin_listening_parts.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Quản lý Listening | Điểm TSA Với Aptis</title>
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
                <strong>Điểm TSA</strong>
                <span>với Aptis</span>
            </div>
        </div>

        <a class="side-link" href="{% url 'dashboard' %}">🎧 Tổng quan Admin</a>
        <a class="side-link active" href="{% url 'admin_listening_parts' %}">🎧 Quản lý câu hỏi Listening</a>
        <a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt học viên</a>
        <a class="side-link" href="/admin/core/lesson/">📚 Quản lý bài học</a>
        <a class="side-link" href="/admin/core/securityalert/">🛡️ Cảnh báo bảo mật</a>
        <a class="side-link" href="{% url 'listening' %}">👀 Xem giao diện học viên</a>
        <a class="side-link logout" href="{% url 'logout' %}">🚪 Đăng xuất</a>
    </aside>

    <main class="admin-main">
        <header class="admin-header">
            <div>
                <p class="eyebrow">Listening Bank</p>
                <h1>Quản lý câu hỏi Listening</h1>
                <p class="muted">Chọn từng Part để khai thác sâu. Trước mắt hoàn thiện Part 1.</p>
            </div>
            <a class="primary-btn" href="{% url 'dashboard' %}">← Về tổng quan</a>
        </header>

        <section class="parts-grid">
            <a class="part-card active" href="{% url 'admin_part1_questions' %}">
                <div class="part-icon">1</div>
                <div>
                    <h2>Part 1</h2>
                    <p>Cập nhật hàng loạt câu hỏi, audio, đáp án và transcript.</p>
                    <strong>{{ part_counts.1 }} câu hỏi</strong>
                </div>
            </a>

            <div class="part-card locked">
                <div class="part-icon">2</div>
                <div>
                    <h2>Part 2</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện Part 1.</p>
                    <strong>{{ part_counts.2 }} câu hỏi</strong>
                </div>
            </div>

            <div class="part-card locked">
                <div class="part-icon">3</div>
                <div>
                    <h2>Part 3</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện Part 1.</p>
                    <strong>{{ part_counts.3 }} câu hỏi</strong>
                </div>
            </div>

            <div class="part-card locked">
                <div class="part-icon">4</div>
                <div>
                    <h2>Part 4</h2>
                    <p>Sẽ thiết kế sau khi hoàn thiện Part 1.</p>
                    <strong>{{ part_counts.4 }} câu hỏi</strong>
                </div>
            </div>
        </section>
    </main>
</div>
</body>
</html>
''', encoding="utf-8")

print("DA_TAO_LAI_TRANG_4_PART")
