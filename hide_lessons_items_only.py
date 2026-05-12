from pathlib import Path
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_hide_lesson_items_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# CSS ẩn đúng mục Quản lý bài học / lesson
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
css_file = css_dir / "hide_lessons_items.css"

css_file.write_text(r'''
/* Hide only Lessons / Quản lý bài học items */
a[href*="lesson"],
a[href*="bai-hoc"],
a[href*="lessons"],
button[href*="lesson"],
.lesson-card,
.lessons-card,
.admin-lessons-card,
[data-section*="lesson"],
[data-card*="lesson"] {
    display: none !important;
}

/* Hide dashboard cards/blocks that contain only lesson management via modern browser selector */
.card:has(a[href*="lesson"]),
.card:has(a[href*="lessons"]),
.dashboard-card:has(a[href*="lesson"]),
.dashboard-card:has(a[href*="lessons"]),
.admin-card:has(a[href*="lesson"]),
.admin-card:has(a[href*="lessons"]),
section:has(a[href*="lesson"]),
section:has(a[href*="lessons"]) {
    display: none !important;
}
''', encoding="utf-8")

# JS phụ để ẩn chính xác các khối có chữ Quản lý bài học, không ảnh hưởng mục khác
js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)
js_file = js_dir / "hide_lessons_items.js"

js_file.write_text(r'''
document.addEventListener("DOMContentLoaded", function () {
    const badTexts = [
        "Quản lý bài học",
        "Bài học",
        "Thêm, sửa và quản lý bài học hiển thị cho học viên",
        "Chọn Bài học để thay đổi"
    ];

    const candidates = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .admin-card, section, article, .tile, .menu-link, .side-link, .sidebar-link"));

    candidates.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isLessonHref = href.includes("lesson") || href.includes("bai-hoc") || href.includes("lessons");
        const isLessonText = badTexts.some(t => text.includes(t));

        if (isLessonHref || isLessonText) {
            let target = el;

            // Nếu là link trong card dashboard thì ẩn cả card cha
            const card = el.closest(".card, .dashboard-card, .admin-card, section, article, .tile");
            if (card && !card.innerText.includes("Duyệt học viên") && !card.innerText.includes("Cảnh báo bảo mật")) {
                target = card;
            }

            target.style.setProperty("display", "none", "important");
        }
    });
});
''', encoding="utf-8")

# Nạp CSS/JS vào tất cả template html chính
templates = [p for p in Path("templates").rglob("*.html")]

for path in templates:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "hide_lessons_items.css" not in text and "</head>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/hide_lessons_items.css\' %}">\n</head>'
        )

    if "hide_lessons_items.js" not in text and "</body>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</body>",
            '    <script src="{% static \'js/hide_lessons_items.js\' %}"></script>\n</body>'
        )

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Updated:", path)

print("DONE")
print("Backup:", backup_dir)
print("CSS:", css_file)
print("JS:", js_file)
