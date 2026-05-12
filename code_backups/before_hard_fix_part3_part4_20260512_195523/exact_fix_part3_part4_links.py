from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== FIX PART 3 / PART 4 LINKS EXACTLY ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_exact_fix_part3_part4_links_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Gỡ JS sửa link cũ vì có thể can thiệp sai
bad_js = Path("static/js/fix_part_card_links.js")
if bad_js.exists():
    shutil.copy2(bad_js, backup_dir / "fix_part_card_links.js")
    bad_js.unlink()
    print("Deleted old JS:", bad_js)

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    text = re.sub(r'\s*<script[^>]+fix_part_card_links\.js[^>]*></script>\s*', "\n", text)

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Removed old JS reference:", path)

# 2) Sửa đúng file chọn Part: chỉ sửa trong đoạn của Part 3 và Part 4
def fix_part_slice(text, part_marker, next_marker, target_href, target_label):
    start = text.find(part_marker)
    if start == -1:
        return text

    end = text.find(next_marker, start + len(part_marker)) if next_marker else -1
    if end == -1:
        end = len(text)

    before = text[:start]
    seg = text[start:end]
    after = text[end:]

    # Trong đúng block của Part này: mọi link mở nhầm Part 2/1/3/4 đều đổi về đúng Part
    seg = re.sub(r'href=(["\'])/dashboard/part-[1234]/\1', rf'href=\1{target_href}\1', seg)
    seg = re.sub(r'href=(["\'])/dashboard/part-[1234]/(["\'])', rf'href=\1{target_href}\2', seg)

    # Nếu dùng URL không có dashboard
    seg = re.sub(r'href=(["\'])/part-[1234]/\1', rf'href=\1{target_href}\1', seg)
    seg = re.sub(r'href=(["\'])/part-[1234]/(["\'])', rf'href=\1{target_href}\2', seg)

    # Sửa label nút
    seg = re.sub(r'Mở Part\s*[1234]', target_label, seg)

    return before + seg + after

changed = []

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Chỉ đụng file có đủ danh sách Part 1-4
    if not all(x in text for x in ["Part 1", "Part 2", "Part 3", "Part 4"]):
        continue

    text = fix_part_slice(text, "Part 3", "Part 4", "/dashboard/part-3/", "Mở Part 3")
    text = fix_part_slice(text, "Part 4", None, "/dashboard/part-4/", "Mở Part 4")

    if text != original:
        shutil.copy2(path, backup_dir / ("fixed__" + str(path).replace("\\", "__").replace("/", "__")))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Changed files:")
for f in changed:
    print("-", f)

# 3) In report để kiểm tra lại nút/link hiện tại
report = Path("part_card_link_report.txt")
lines = ["=== PART CARD LINK REPORT ==="]

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if all(x in text for x in ["Part 1", "Part 2", "Part 3", "Part 4"]):
        lines.append(f"\nFILE: {path}")
        for m in re.finditer(r'(?is).{0,120}(Part [1234]).{0,220}(href=[^ >]+|Mở Part [1234]).{0,120}', text):
            lines.append(re.sub(r'\s+', ' ', m.group(0)).strip())

report.write_text("\n".join(lines), encoding="utf-8")
print("Report:", report)
print("DONE")
print("Backup:", backup_dir)
