from pathlib import Path
import shutil
from datetime import datetime

print("=== LOCK PART 2, FOCUS PART 3 ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_focus_part3_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

for folder in ["templates", "static"]:
    p = Path(folder)
    if p.exists():
        shutil.copytree(p, backup_dir / folder, dirs_exist_ok=True)

note = Path("code_backups") / "LOCKED_UI_NOTES.txt"
old = note.read_text(encoding="utf-8", errors="ignore") if note.exists() else ""
note.write_text(
    old +
    "\n\n=== PART 3 START ===\n"
    f"Time: {datetime.now()}\n"
    "- Part 2 student UI approved.\n"
    "- Part 2 admin UI approved/kept.\n"
    "- Next work: Part 3 only.\n",
    encoding="utf-8"
)

css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)

css_file = css_dir / "focus_part3_only.css"
css_file.write_text(r'''
/* Focus Part 3 only - do not change Part 2 UI */
.tsa-part3-focus {
    transform: scale(1.025) !important;
    box-shadow: 0 18px 42px rgba(220, 0, 35, 0.22) !important;
    border: 2px solid rgba(255, 40, 80, 0.65) !important;
    position: relative !important;
}

.tsa-part3-focus::after {
    content: "Đang thiết kế";
    position: absolute;
    top: 10px;
    right: 10px;
    background: #e63946;
    color: #fff;
    font-weight: 900;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    pointer-events: none;
}

.tsa-part-not-active {
    opacity: 0.52 !important;
    filter: grayscale(0.35) !important;
}
''', encoding="utf-8")

js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)

js_file = js_dir / "focus_part3_only.js"
js_file.write_text(r'''
document.addEventListener("DOMContentLoaded", function () {
    const cards = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .part-card, .tile, article, section"));

    cards.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isPart3 = text.includes("Part 3") || href.includes("part-3");
        const isPart1 = text.includes("Part 1") || href.includes("part-1");
        const isPart2 = text.includes("Part 2") || href.includes("part-3");
        const isPart4 = text.includes("Part 4") || href.includes("part-4");

        if (isPart3) {
            el.classList.add("tsa-part3-focus");
        } else if (isPart1 || isPart2 || isPart4) {
            el.classList.add("tsa-part-not-active");
        }
    });
});
''', encoding="utf-8")

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "{% load static %}" not in text:
        text = "{% load static %}\n" + text

    if "focus_part3_only.css" not in text and "</head>" in text:
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/focus_part3_only.css\' %}">\n</head>'
        )

    if "focus_part3_only.js" not in text and "</body>" in text:
        text = text.replace(
            "</body>",
            '    <script src="{% static \'js/focus_part3_only.js\' %}"></script>\n</body>'
        )

    if text != original:
        path.write_text(text, encoding="utf-8")

print("DONE")
print("Backup:", backup_dir)
