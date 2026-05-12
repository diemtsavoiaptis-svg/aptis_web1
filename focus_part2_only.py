from pathlib import Path
import shutil
from datetime import datetime

print("=== LOCK ALL PARTS EXCEPT PART 2 ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_focus_part2_only_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

css_dir = Path("static/css")
js_dir = Path("static/js")
css_dir.mkdir(parents=True, exist_ok=True)
js_dir.mkdir(parents=True, exist_ok=True)

css_file = css_dir / "focus_part2_only.css"
js_file = js_dir / "focus_part2_only.js"

css_file.write_text(r'''
/* Focus only Part 2 - lock Part 1/3/4 visually */
.tsa-part-locked {
    opacity: 0.42 !important;
    filter: grayscale(0.55) !important;
    cursor: not-allowed !important;
    position: relative !important;
}

.tsa-part-locked::after {
    content: "Đã khóa";
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(120, 0, 20, 0.9);
    color: #fff;
    font-weight: 900;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    pointer-events: none;
}

.tsa-part2-focus {
    transform: scale(1.025) !important;
    box-shadow: 0 18px 42px rgba(220, 0, 35, 0.22) !important;
    border: 2px solid rgba(255, 40, 80, 0.65) !important;
}

.tsa-part2-focus::after {
    content: "Đang thiết kế";
    position: absolute;
    top: 10px;
    right: 10px;
    background: #ff244f;
    color: #fff;
    font-weight: 900;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    pointer-events: none;
}
''', encoding="utf-8")

js_file.write_text(r'''
document.addEventListener("DOMContentLoaded", function () {
    const lockTexts = ["Part 1", "Part 3", "Part 4"];
    const focusTexts = ["Part 2"];

    const clickable = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .part-card, .tile, article, section"));

    clickable.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isPart1 = text.includes("Part 1") || href.includes("part-1") || href.endsWith("/listening/");
        const isPart3 = text.includes("Part 3") || href.includes("part-3");
        const isPart4 = text.includes("Part 4") || href.includes("part-4");
        const isPart2 = text.includes("Part 2") || href.includes("part-2");

        if (isPart2) {
            el.classList.add("tsa-part2-focus");
            return;
        }

        if (isPart1 || isPart3 || isPart4) {
            el.classList.add("tsa-part-locked");

            if (el.tagName.toLowerCase() === "a") {
                el.setAttribute("data-old-href", el.getAttribute("href") || "");
                el.removeAttribute("href");
            }

            el.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                alert("Mục này đang khóa. Hiện tại chỉ thiết kế sâu Part 2.");
                return false;
            }, true);
        }
    });
});
''', encoding="utf-8")

# Inject CSS/JS safely
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "{% load static %}" not in text:
        text = "{% load static %}\n" + text

    if "focus_part2_only.css" not in text and "</head>" in text:
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/focus_part2_only.css\' %}">\n</head>'
        )

    if "focus_part2_only.js" not in text and "</body>" in text:
        text = text.replace(
            "</body>",
            '    <script src="{% static \'js/focus_part2_only.js\' %}"></script>\n</body>'
        )

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Updated:", path)

print("DONE: Part 1/3/4 locked, Part 2 focused.")
print("Backup:", backup_dir)
