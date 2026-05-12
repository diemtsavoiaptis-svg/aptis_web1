from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== FINAL FORCE FIX ONLY PART 3 BUTTON ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_final_force_part3_button_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

skip = ["venv", ".git", "__pycache__", "staticfiles", "media", "code_backups"]
exts = [".html", ".py", ".js"]

def skipped(path):
    return any(s in path.parts for s in skip)

changed = []

# 1) Sửa trực tiếp trong mọi file nguồn: chỉ vùng Part 3 -> trước Part 4
for path in Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in exts or skipped(path):
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Part 3" in text and "Mở Part 2" in text:
        p3 = text.find("Part 3")
        p4 = text.find("Part 4", p3)

        before = text[:p3]
        block = text[p3:p4 if p4 != -1 else len(text)]
        after = text[p4:] if p4 != -1 else ""

        block = block.replace("Mở Part 2", "Mở Part 3")
        block = block.replace('/dashboard/part-2/', '/dashboard/part-3/')
        block = block.replace('"/dashboard/part-2/"', '"/dashboard/part-3/"')
        block = block.replace("'/dashboard/part-2/'", "'/dashboard/part-3/'")
        block = block.replace('"part-2"', '"part-3"')
        block = block.replace("'part-2'", "'part-3'")

        text = before + block + after

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

# 2) Chèn script ép sửa Part 3 trực tiếp vào HTML, tránh cache file static
inline_script = r'''
<script id="force-part3-button-only">
(function () {
    function fixPart3ButtonOnly() {
        const buttons = Array.from(document.querySelectorAll("a, button"));

        buttons.forEach(function (btn) {
            const label = (btn.innerText || btn.textContent || "").trim();
            if (!label.includes("Mở Part")) return;

            let node = btn.parentElement;
            let part3Box = null;

            while (node && node !== document.body) {
                const txt = (node.innerText || node.textContent || "").trim();

                if (txt.includes("Part 3") && !txt.includes("Part 4")) {
                    part3Box = node;
                    break;
                }

                node = node.parentElement;
            }

            if (!part3Box) return;

            btn.textContent = "Mở Part 3";

            if (btn.tagName.toLowerCase() === "a") {
                btn.setAttribute("href", "/dashboard/part-3/");
            } else {
                btn.onclick = function (e) {
                    e.preventDefault();
                    window.location.href = "/dashboard/part-3/";
                };
            }
        });
    }

    document.addEventListener("DOMContentLoaded", fixPart3ButtonOnly);
    window.addEventListener("load", fixPart3ButtonOnly);

    const observer = new MutationObserver(fixPart3ButtonOnly);
    observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        characterData: true
    });

    setInterval(fixPart3ButtonOnly, 500);
})();
</script>
'''

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "force-part3-button-only" in text:
        continue

    # Chỉ chèn vào các template có trang chọn Part
    if all(x in text for x in ["Part 1", "Part 2", "Part 3", "Part 4"]) and "</body>" in text:
        text = text.replace("</body>", inline_script + "\n</body>")

    if text != original:
        shutil.copy2(path, backup_dir / ("inject__" + str(path).replace("\\", "__").replace("/", "__")))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

# 3) Report chính xác file nào còn chứa lỗi
report = Path("final_part3_button_report.txt")
lines = ["=== FINAL PART 3 BUTTON REPORT ==="]

for path in Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in exts or skipped(path):
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")

    if "Part 3" in text and "Mở Part 2" in text:
        lines.append(f"\nSTILL HAS SOURCE ISSUE: {path}")
        for line in text.splitlines():
            if "Part 3" in line or "Mở Part 2" in line or "part-2" in line:
                lines.append(line[:300])

report.write_text("\n".join(lines), encoding="utf-8")

print("Changed files:")
for f in changed:
    print("-", f)

print("Backup:", backup_dir)
print("Report:", report)
print("DONE")
