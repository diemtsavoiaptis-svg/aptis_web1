from pathlib import Path

Path("templates/core/dashboard.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Admin | Điểm TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/admin_panel.css' %}">
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

        <button class="side-link active" data-title="Tổng quan Admin" data-src="">
            🎧 Tổng quan Admin
        </button>

        <button class="side-link" data-title="Quản lý câu hỏi Listening" data-src="/admin/core/listeningquestion/">
            🎧 Quản lý câu hỏi Listening
        </button>

        <button class="side-link" data-title="Duyệt học viên" data-src="/admin/core/studentprofile/">
            ✅ Duyệt học viên
        </button>

        <button class="side-link" data-title="Quản lý bài học" data-src="/admin/core/lesson/">
            📚 Quản lý bài học
        </button>

        <button class="side-link" data-title="Cảnh báo bảo mật" data-src="/admin/core/securityalert/">
            🛡️ Cảnh báo bảo mật
        </button>

        <a class="side-link" href="{% url 'listening' %}">
            👀 Xem giao diện học viên
        </a>

        <a class="side-link logout" href="{% url 'logout' %}">
            🚪 Đăng xuất
        </a>
    </aside>

    <main class="admin-main">
        <header class="admin-header">
            <div>
                <p class="eyebrow">Dashboard quản trị</p>
                <h1 id="panelTitle">Xin chào, {{ request.user.username }}</h1>
                <p class="muted">Bấm menu bên trái, nội dung sẽ hiện ở khung bên phải mà không đổi trang.</p>
            </div>
            <a class="primary-btn" href="/admin/" target="_blank">Mở Django Admin</a>
        </header>

        <section id="overviewPanel" class="overview-panel">
            <div class="quick-grid">
                <button class="quick-card" data-title="Quản lý câu hỏi Listening" data-src="/admin/core/listeningquestion/">
                    <span>🎧</span>
                    <strong>Listening</strong>
                    <small>Thêm/sửa câu hỏi, audio, đáp án và transcript.</small>
                </button>

                <button class="quick-card" data-title="Duyệt học viên" data-src="/admin/core/studentprofile/">
                    <span>✅</span>
                    <strong>Học viên</strong>
                    <small>Duyệt tài khoản học viên mới đăng ký.</small>
                </button>

                <button class="quick-card" data-title="Quản lý bài học" data-src="/admin/core/lesson/">
                    <span>📚</span>
                    <strong>Bài học</strong>
                    <small>Quản lý tài liệu, mô tả và video học tập.</small>
                </button>
            </div>

            <div class="lesson-card">
                <div class="section-head">
                    <div>
                        <h2>Danh sách bài học</h2>
                        <p>Các bài học đang có trong hệ thống.</p>
                    </div>
                    <button class="ghost-btn" data-title="Thêm bài học" data-src="/admin/core/lesson/add/">
                        + Thêm bài học
                    </button>
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
            </div>
        </section>

        <section id="framePanel" class="frame-panel" hidden>
            <div class="frame-toolbar">
                <div>
                    <strong id="frameTitle">Quản lý</strong>
                    <span>Đang hiển thị trong dashboard, không rời khỏi trang.</span>
                </div>
                <button class="ghost-btn" id="backOverview">← Về tổng quan</button>
            </div>

            <iframe id="adminFrame" title="Admin content"></iframe>
        </section>
    </main>
</div>

<script>
(function () {
    const links = document.querySelectorAll("[data-src]");
    const overviewPanel = document.getElementById("overviewPanel");
    const framePanel = document.getElementById("framePanel");
    const adminFrame = document.getElementById("adminFrame");
    const frameTitle = document.getElementById("frameTitle");
    const panelTitle = document.getElementById("panelTitle");
    const backOverview = document.getElementById("backOverview");

    function setActive(button) {
        document.querySelectorAll(".side-link").forEach(x => x.classList.remove("active"));
        if (button && button.classList.contains("side-link")) {
            button.classList.add("active");
        }
    }

    function openPanel(title, src, button) {
        if (!src) {
            overviewPanel.hidden = false;
            framePanel.hidden = true;
            adminFrame.removeAttribute("src");
            panelTitle.textContent = "Xin chào, {{ request.user.username }}";
            setActive(button);
            return;
        }

        overviewPanel.hidden = true;
        framePanel.hidden = false;
        adminFrame.src = src;
        frameTitle.textContent = title || "Quản lý";
        panelTitle.textContent = title || "Quản lý";
        setActive(button);
    }

    links.forEach(btn => {
        btn.addEventListener("click", function () {
            openPanel(this.dataset.title, this.dataset.src, this);
        });
    });

    backOverview.addEventListener("click", function () {
        const first = document.querySelector(".side-link[data-src='']");
        openPanel("", "", first);
    });
})();
</script>
</body>
</html>
''', encoding="utf-8")

css_dir = Path("static/core/css")
css_dir.mkdir(parents=True, exist_ok=True)

Path("static/core/css/admin_panel.css").write_text(r''':root {
    --red: #d60018;
    --red-dark: #600006;
    --red-mid: #8d0b16;
    --red-soft: #fff0f2;
    --line: #ffd1d6;
    --text: #280006;
    --muted: #687084;
    --white: #fff;
    --shadow: 0 20px 50px rgba(96,0,6,.10);
}

* { box-sizing: border-box; }

body.admin-page {
    margin: 0;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: linear-gradient(135deg, #fff8f8, #ffecef);
    color: var(--text);
}

a { color: inherit; text-decoration: none; }

.admin-shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 285px 1fr;
}

.admin-sidebar {
    background: linear-gradient(180deg, #620006 0%, #8b000c 100%);
    padding: 24px 18px;
    color: white;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow: auto;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
}

.brand-logo {
    width: 54px;
    height: 54px;
    border-radius: 18px;
    background: var(--red);
    display: grid;
    place-items: center;
    font-weight: 1000;
    font-size: 22px;
    box-shadow: 0 14px 30px rgba(0,0,0,.18);
}

.brand strong {
    display: block;
    font-size: 23px;
    line-height: 1.05;
}

.brand span {
    display: block;
    margin-top: 4px;
    opacity: .9;
}

.side-link {
    width: 100%;
    display: flex;
    align-items: center;
    border: 0;
    margin: 10px 0;
    padding: 15px 17px;
    border-radius: 16px;
    background: rgba(255,255,255,.10);
    color: white;
    text-align: left;
    font-weight: 900;
    font-size: 16px;
    line-height: 1.35;
    cursor: pointer;
}

.side-link:hover,
.side-link.active {
    background: var(--red);
    box-shadow: 0 12px 25px rgba(0,0,0,.18);
}

.side-link.logout {
    margin-top: 22px;
    background: rgba(255,255,255,.14);
}

.admin-main {
    padding: 28px;
    min-width: 0;
}

.admin-header,
.lesson-card,
.frame-panel,
.quick-card {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 28px;
    box-shadow: var(--shadow);
}

.admin-header {
    padding: 28px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 24px;
}

.eyebrow {
    margin: 0 0 10px;
    color: var(--red);
    font-weight: 1000;
    text-transform: uppercase;
    letter-spacing: .08em;
}

h1 {
    margin: 0 0 12px;
    font-size: clamp(30px, 4vw, 44px);
    color: var(--text);
}

h2, h3 { color: var(--text); }

.muted,
.admin-header p,
.section-head p {
    color: var(--muted);
}

.primary-btn,
.ghost-btn {
    border: 0;
    border-radius: 16px;
    padding: 13px 20px;
    font-weight: 950;
    cursor: pointer;
    display: inline-flex;
    justify-content: center;
    align-items: center;
}

.primary-btn {
    background: var(--red);
    color: white;
    box-shadow: 0 14px 25px rgba(214,0,24,.18);
}

.ghost-btn {
    background: var(--red-soft);
    color: var(--red-dark);
    border: 1px solid var(--line);
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 22px;
    margin-bottom: 24px;
}

.quick-card {
    padding: 28px;
    text-align: left;
    cursor: pointer;
    min-height: 210px;
}

.quick-card span {
    display: block;
    font-size: 38px;
    margin-bottom: 18px;
}

.quick-card strong {
    display: block;
    font-size: 24px;
    margin-bottom: 12px;
    color: var(--red-dark);
}

.quick-card small {
    display: block;
    font-size: 16px;
    line-height: 1.5;
    color: #1f2937;
}

.quick-card:hover {
    transform: translateY(-2px);
    border-color: #ff9aa5;
}

.lesson-card {
    padding: 28px;
}

.section-head,
.frame-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 20px;
}

.lesson-list {
    display: grid;
    gap: 14px;
}

.lesson-item,
.empty-box {
    border: 1px solid #f4d6d9;
    background: #fffafa;
    border-radius: 18px;
    padding: 18px 20px;
}

.lesson-item h3 {
    margin: 0 0 10px;
}

.lesson-item p {
    color: #374151;
    line-height: 1.6;
}

.frame-panel {
    padding: 18px;
}

.frame-toolbar {
    padding: 6px 4px 18px;
}

.frame-toolbar strong {
    display: block;
    color: var(--red-dark);
    font-size: 22px;
}

.frame-toolbar span {
    display: block;
    color: var(--muted);
    font-size: 14px;
    margin-top: 4px;
}

#adminFrame {
    width: 100%;
    height: calc(100vh - 190px);
    border: 1px solid var(--line);
    border-radius: 20px;
    background: white;
}

@media (max-width: 980px) {
    .admin-shell { grid-template-columns: 1fr; }
    .admin-sidebar {
        position: relative;
        height: auto;
    }
    .quick-grid { grid-template-columns: 1fr; }
    .admin-header,
    .section-head,
    .frame-toolbar {
        flex-direction: column;
        align-items: stretch;
    }
}
''', encoding="utf-8")

print("DA_SUA_DASHBOARD_ADMIN_IFRAME")
