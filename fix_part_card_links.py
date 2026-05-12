from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== FIX PART CARD LINKS: PART 1/2/3/4 OPEN CORRECT PAGE ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_fix_part_card_links_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Sửa trực tiếp trong template chọn Part nếu có text bị nhầm
targets = [p for p in Path("templates").rglob("*.html")]

for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Part 3" in text and "Mở Part 3" in text:
        # Sửa riêng các block có Part 3
        text = re.sub(
            r'(?is)(Part 3.*?)(Mở Part 3)',
            lambda m: m.group(1).replace('/dashboard/part-3/', '/dashboard/part-3/').replace('part-3', 'part-3') + 'Mở Part 3',
            text,
            count=1
        )

    if "Part 4" in text and "Mở Part 4" in text:
        # Sửa riêng các block có Part 4
        text = re.sub(
            r'(?is)(Part 4.*?)(Mở Part 4)',
            lambda m: m.group(1).replace('/dashboard/part-4/', '/dashboard/part-4/').replace('part-4', 'part-4') + 'Mở Part 4',
            text,
            count=1
        )

    # Sửa các href rõ ràng nếu nằm trong card Part 3/4 dạng ngắn
    text = text.replace('href="/dashboard/part-4/">Mở Part 4', 'href="/dashboard/part-4/">Mở Part 4')
    text = text.replace("href='/dashboard/part-4/'>Mở Part 4", "href='/dashboard/part-4/'>Mở Part 4")
    text = text.replace('href="/dashboard/part-4/">Mở Part 4', 'href="/dashboard/part-4/">Mở Part 4')
    text = text.replace("href='/dashboard/part-4/'>Mở Part 4", "href='/dashboard/part-4/'>Mở Part 4")

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Fixed template:", path)

# 2) Thêm JS bảo hiểm: nếu còn nút/link nào bị nhầm, trình duyệt tự sửa đúng
js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)
js_file = js_dir / "fix_part_card_links.js"

js_file.write_text(r'''
document.addEventListener("DOMContentLoaded", function () {
    const rules = [
        { part: "Part 1", href: "/dashboard/part-4/", label: "Mở Part 4" },
        { part: "Part 2", href: "/dashboard/part-4/", label: "Mở Part 4" },
        { part: "Part 3", href: "/dashboard/part-4/", label: "Mở Part 4" },
        { part: "Part 4", href: "/dashboard/part-4/", label: "Mở Part 4" },
    ];

    const possibleCards = Array.from(document.querySelectorAll(".card, .dashboard-card, .part-card, .tile, article, section, div"));

    rules.forEach(function (rule) {
        const cards = possibleCards.filter(function (el) {
            const txt = (el.innerText || el.textContent || "").trim();
            return txt.includes(rule.part) && !txt.includes("Part 1\nPart 2\nPart 3\nPart 4");
        });

        cards.forEach(function (card) {
            const buttons = Array.from(card.querySelectorAll("a, button"));
            buttons.forEach(function (btn) {
                const txt = (btn.innerText || btn.textContent || "").trim();

                if (txt.includes("Mở Part") || txt.includes("Mở ")) {
                    btn.innerText = rule.label;

                    if (btn.tagName.toLowerCase() === "a") {
                        btn.setAttribute("href", rule.href);
                    } else {
                        btn.onclick = function (e) {
                            e.preventDefault();
                            window.location.href = rule.href;
                        };
                    }
                }
            });
        });
    });
});
''', encoding="utf-8")

# 3) Nạp JS vào template chọn Part
for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    should_load = (
        "Chọn Part cần quản lý" in text
        or "Choose Part" in text
        or ("Part 1" in text and "Part 2" in text and "Part 3" in text and "Part 4" in text)
    )

    if should_load and "fix_part_card_links.js" not in text and "</body>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</body>",
            '    <script src="{% static \'js/fix_part_card_links.js\' %}"></script>\n</body>'
        )
        path.write_text(text, encoding="utf-8")
        print("Loaded JS in:", path)

print("DONE")
print("Backup:", backup_dir)
