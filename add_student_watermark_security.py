from pathlib import Path
import shutil
from datetime import datetime

print("=== ADD STUDENT WATERMARK SECURITY FOR ALL PARTS ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_student_watermark_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Create watermark partial
partial_dir = Path("templates/core")
partial_dir.mkdir(parents=True, exist_ok=True)
partial = partial_dir / "_student_watermark.html"

partial.write_text(r'''{% if request.user.is_authenticated %}
<div
    id="tsaStudentWatermark"
    class="tsa-student-watermark"
    data-user-id="{{ request.user.id }}"
    data-user-name="{{ request.user.get_username }}"
    data-user-email="{{ request.user.email|default:request.user.get_username }}"
></div>
{% endif %}
''', encoding="utf-8")

# 2) Create CSS
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
css_file = css_dir / "student_watermark_security.css"

css_file.write_text(r'''
/* Student watermark security */
.tsa-student-watermark {
    position: fixed;
    inset: 0;
    z-index: 999999;
    pointer-events: none;
    opacity: 1;
    overflow: hidden;
}

.tsa-student-watermark::before {
    content: attr(data-watermark-text);
    position: absolute;
    inset: -20%;
    display: block;
    white-space: pre;
    font-size: 18px;
    font-weight: 800;
    line-height: 5.5;
    letter-spacing: 1px;
    color: rgba(160, 0, 24, 0.115);
    transform: rotate(-22deg);
    text-transform: uppercase;
    word-spacing: 26px;
}

/* Prevent easy selecting/dragging in student practice screens */
body.tsa-student-secure {
    -webkit-user-select: none;
    user-select: none;
}

body.tsa-student-secure img,
body.tsa-student-secure video,
body.tsa-student-secure audio {
    -webkit-user-drag: none;
    user-drag: none;
}
''', encoding="utf-8")

# 3) Create JS
js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)
js_file = js_dir / "student_watermark_security.js"

js_file.write_text(r'''
(function () {
    function repeatText(text, count) {
        let out = "";
        for (let i = 0; i < count; i++) {
            out += text + "     ";
        }
        return out;
    }

    document.addEventListener("DOMContentLoaded", function () {
        const wm = document.getElementById("tsaStudentWatermark");
        if (!wm) return;

        const userId = wm.dataset.userId || "NO-ID";
        const email = wm.dataset.userEmail || wm.dataset.userName || "STUDENT";
        const now = new Date().toLocaleString("vi-VN");

        const mark = `ID ${userId} - ${email} - ${now}`;
        wm.setAttribute("data-watermark-text", repeatText(mark, 80));

        document.body.classList.add("tsa-student-secure");

        // Light deterrents
        document.addEventListener("contextmenu", function (e) {
            e.preventDefault();
        });

        document.addEventListener("keydown", function (e) {
            const key = (e.key || "").toLowerCase();
            if (
                e.key === "F12" ||
                (e.ctrlKey && e.shiftKey && ["i", "j", "c"].includes(key)) ||
                (e.ctrlKey && ["u", "s", "p"].includes(key))
            ) {
                e.preventDefault();
                return false;
            }
        });
    });
})();
''', encoding="utf-8")

# 4) Inject only into student/practice/listening templates
target_keywords = [
    "listening",
    "student",
    "part2",
    "part3",
    "part4",
]

targets = []
for path in Path("templates").rglob("*.html"):
    name = str(path).lower()
    if any(k in name for k in target_keywords):
        targets.append(path)

for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "{% load static %}" not in text:
        text = "{% load static %}\n" + text

    if "student_watermark_security.css" not in text and "</head>" in text:
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/student_watermark_security.css\' %}">\n</head>'
        )

    if "_student_watermark.html" not in text and "</body>" in text:
        text = text.replace(
            "</body>",
            '    {% include "core/_student_watermark.html" %}\n'
            '    <script src="{% static \'js/student_watermark_security.js\' %}"></script>\n'
            '</body>'
        )

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Watermark injected:", path)

print("DONE")
print("Backup:", backup_dir)
print("CSS:", css_file)
print("JS:", js_file)
