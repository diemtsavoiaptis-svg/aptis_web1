from pathlib import Path
import re
import shutil
import unicodedata
from datetime import datetime

print("=== HARD FIX PART 3 / PART 4 CARDS EVERYWHERE ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_hard_fix_part3_part4_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

exts = {".html", ".py", ".js", ".css"}
skip_dirs = {"venv", ".git", "__pycache__", "staticfiles", "media", "code_backups"}

def should_skip(path: Path):
    return any(part in skip_dirs for part in path.parts)

def repair_vietnamese(s: str) -> str:
    s = unicodedata.normalize("NFC", s)

    # sửa đúng lỗi đang thấy: tiế ́ p / chi tiế ́ t
    patterns = [
        (r"tiế\s*[\u0300-\u036f]\s*p", "tiếp"),
        (r"tiê\s*[\u0300-\u036f]\s*p", "tiếp"),
        (r"tiế\s+p", "tiếp"),
        (r"tiế\s+p", "tiếp"),
        (r"chi\s+tiế\s*[\u0300-\u036f]\s*t", "chi tiết"),
        (r"chi\s+tiê\s*[\u0300-\u036f]\s*t", "chi tiết"),
        (r"chi\s+tiế\s+t", "chi tiết"),
        (r"chi\s+tiế\s+t", "chi tiết"),
    ]

    for pat, repl in patterns:
        s = re.sub(pat, repl, s)

    s = s.replace("tiế ́ p", "tiếp")
    s = s.replace("tiế ́p", "tiếp")
    s = s.replace("tiế p", "tiếp")
    s = s.replace("chi tiế ́ t", "chi tiết")
    s = s.replace("chi tiế ́t", "chi tiết")
    s = s.replace("chi tiế t", "chi tiết")

    return s

def fix_block(block: str, part_num: int) -> str:
    block = repair_vietnamese(block)

    correct_label = f"Mở Part {part_num}"
    correct_href = f"/dashboard/part-{part_num}/"

    # Sửa label sai
    block = re.sub(r"Mở\s+Part\s+[1234]", correct_label, block)

    # Sửa href sai dạng dashboard
    block = re.sub(
        r'(["\'])/dashboard/part-[1234]/(["\'])',
        rf'\1{correct_href}\2',
        block
    )

    # Sửa href sai dạng ngắn
    block = re.sub(
        r'(["\'])/part-[1234]/(["\'])',
        rf'\1{correct_href}\2',
        block
    )

    # Sửa reverse/url text nếu có
    block = block.replace("dashboard/part-2", f"dashboard/part-{part_num}")
    block = block.replace("part-2", f"part-{part_num}") if part_num in [3,4] and "Part " + str(part_num) in block else block

    return block

changed = []
report_lines = ["=== HARD FIX REPORT ==="]

for path in Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in exts or should_skip(path):
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Normalize toàn file
    text = repair_vietnamese(text)

    # Nếu file có đủ Part 3/4 thì sửa theo từng vùng
    if "Part 3" in text or "Part 4" in text:
        # Sửa block Part 3: từ Part 3 tới Part 4 nếu có
        p3 = text.find("Part 3")
        p4 = text.find("Part 4")

        if p3 != -1 and p4 != -1 and p3 < p4:
            before = text[:p3]
            block3 = text[p3:p4]
            block4 = text[p4:]

            block3 = fix_block(block3, 3)
            block4 = fix_block(block4, 4)

            text = before + block3 + block4

        elif p3 != -1:
            text = text[:p3] + fix_block(text[p3:], 3)

        elif p4 != -1:
            text = text[:p4] + fix_block(text[p4:], 4)

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

# Tạo thêm JS ép sửa ngay trên trình duyệt nếu template còn cache/sinh động
js_dir = Path("static/js")
js_dir.mkdir(parents=True, exist_ok=True)
js_file = js_dir / "force_fix_part3_part4_cards.js"
js_file.write_text(r'''
document.addEventListener("DOMContentLoaded", function () {
    function cleanText(s) {
        return (s || "")
            .replace(/tiế\s*[\u0300-\u036f]\s*p/g, "tiếp")
            .replace(/tiê\s*[\u0300-\u036f]\s*p/g, "tiếp")
            .replace(/tiế\s+p/g, "tiếp")
            .replace(/chi\s+tiế\s*[\u0300-\u036f]\s*t/g, "chi tiết")
            .replace(/chi\s+tiê\s*[\u0300-\u036f]\s*t/g, "chi tiết")
            .replace(/chi\s+tiế\s+t/g, "chi tiết");
    }

    document.querySelectorAll("*").forEach(function (el) {
        if (el.children.length === 0 && el.textContent) {
            const fixed = cleanText(el.textContent);
            if (fixed !== el.textContent) el.textContent = fixed;
        }
    });

    const cards = Array.from(document.querySelectorAll(".card, .dashboard-card, .part-card, article, section, div"));

    cards.forEach(function (card) {
        const txt = (card.innerText || card.textContent || "");

        if (txt.includes("Part 3")) {
            card.querySelectorAll("a, button").forEach(function (btn) {
                const t = (btn.innerText || btn.textContent || "");
                if (t.includes("Mở Part")) {
                    btn.innerText = "Mở Part 3";
                    if (btn.tagName.toLowerCase() === "a") btn.href = "/dashboard/part-3/";
                    btn.onclick = function(e) {
                        if (btn.tagName.toLowerCase() !== "a") {
                            e.preventDefault();
                            window.location.href = "/dashboard/part-3/";
                        }
                    };
                }
            });
        }

        if (txt.includes("Part 4")) {
            card.querySelectorAll("a, button").forEach(function (btn) {
                const t = (btn.innerText || btn.textContent || "");
                if (t.includes("Mở Part")) {
                    btn.innerText = "Mở Part 4";
                    if (btn.tagName.toLowerCase() === "a") btn.href = "/dashboard/part-4/";
                    btn.onclick = function(e) {
                        if (btn.tagName.toLowerCase() !== "a") {
                            e.preventDefault();
                            window.location.href = "/dashboard/part-4/";
                        }
                    };
                }
            });
        }
    });
});
''', encoding="utf-8")

# Nạp JS vào đúng template có Part 1-4
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if all(x in text for x in ["Part 1", "Part 2", "Part 3", "Part 4"]):
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text

        if "force_fix_part3_part4_cards.js" not in text and "</body>" in text:
            text = text.replace(
                "</body>",
                '    <script src="{% static \'js/force_fix_part3_part4_cards.js\' %}"></script>\n</body>'
            )

    if text != original:
        shutil.copy2(path, backup_dir / ("inject__" + str(path).replace("\\", "__").replace("/", "__")))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

# Report
for path in Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in exts or should_skip(path):
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if ("Part 3" in text or "Part 4" in text) and ("Mở Part 2" in text or "tiế ́" in text or "chi tiế ́" in text):
        report_lines.append(f"\nSTILL CHECK: {path}")
        for line in text.splitlines():
            if "Mở Part 2" in line or "tiế" in line or "chi tiế" in line:
                report_lines.append(line[:300])

Path("part3_part4_hard_fix_report.txt").write_text("\n".join(report_lines), encoding="utf-8")

print("Changed files:")
for f in changed:
    print("-", f)

print("Backup:", backup_dir)
print("Report: part3_part4_hard_fix_report.txt")
print("DONE")
