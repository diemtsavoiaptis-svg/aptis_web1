from pathlib import Path
import shutil
from datetime import datetime

print("=== MAKE WATERMARK SAME FOR PART 1/2/3/4 ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_equal_watermark_all_parts_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Ghi lại CSS watermark đồng đều cho cả 4 part
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
css_file = css_dir / "student_watermark_security.css"

if css_file.exists():
    shutil.copy2(css_file, backup_dir / "student_watermark_security.css")

css_file.write_text(r'''
/* Strong equal watermark for Part 1 / Part 2 / Part 3 / Part 4 */
.tsa-student-watermark {
    position: fixed !important;
    inset: 0 !important;
    z-index: 2147483647 !important;
    pointer-events: none !important;
    opacity: 1 !important;
    overflow: hidden !important;
}

.tsa-student-watermark::before {
    content: attr(data-watermark-text) !important;
    position: absolute !important;
    inset: -30% !important;
    display: block !important;
    white-space: pre !important;
    font-size: 19px !important;
    font-weight: 900 !important;
    line-height: 5.4 !important;
    letter-spacing: 1px !important;
    color: rgba(155, 0, 24, 0.20) !important;
    transform: rotate(-22deg) !important;
    text-transform: uppercase !important;
    word-spacing: 28px !important;
    text-shadow: 0 0 1px rgba(155, 0, 24, 0.18) !important;
}

/* Make watermark visible above white/pink cards in all student part pages */
.student-page .tsa-student-watermark,
.listening-page .tsa-student-watermark,
.part2-page .tsa-student-watermark,
.part3-page .tsa-student-watermark,
.part4-page .tsa-student-watermark,
body .tsa-student-watermark {
    display: block !important;
    visibility: visible !important;
}

/* Light security deterrent */
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

# 2) Ghi lại JS tạo chữ watermark dày giống Part 1
js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)
js_file = js_dir / "student_watermark_security.js"

if js_file.exists():
    shutil.copy2(js_file, backup_dir / "student_watermark_security.js")

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
        const now = new Date().toLocaleDateString("vi-VN");

        const mark = `ID ${userId} - ${email} - ${now}`;
        wm.setAttribute("data-watermark-text", repeatText(mark, 120));

        document.body.classList.add("tsa-student-secure");

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

# 3) Đảm bảo Part 2/3/4 student templates đều có include watermark + CSS/JS
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

target_names = [
    "listening.html",
    "listening_part2.html",
    "listening_parts.html",
    "student_part2_choose_version.html",
    "student_part34.html",
    "student_part3_listening.html",
    "part3_student_only.html",
    "part3_red_student.html",
    "part3_force_student.html",
]

for path in Path("templates").rglob("*.html"):
    if path.name not in target_names:
        continue

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

    if "student_watermark_security.js" not in text and "</body>" in text:
        text = text.replace(
            "</body>",
            '    <script src="{% static \'js/student_watermark_security.js\' %}"></script>\n</body>'
        )

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Updated:", path)

print("DONE: Part 1/2/3/4 watermark made equal.")
print("Backup:", backup_dir)
