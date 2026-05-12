from pathlib import Path
import re
import shutil
import unicodedata
from datetime import datetime

print("=== FIX PART 3 / PART 4 TEXT + LINKS ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_fix_part3_part4_text_links_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

def fix_part_block(text, part_num, next_part_num=None):
    marker = f"Part {part_num}"
    next_marker = f"Part {next_part_num}" if next_part_num else None

    start = text.find(marker)
    if start == -1:
        return text

    end = text.find(next_marker, start + len(marker)) if next_marker else -1
    if end == -1:
        end = len(text)

    before = text[:start]
    block = text[start:end]
    after = text[end:]

    # Chuẩn hóa Unicode dựng sẵn NFC trong riêng block Part này
    block = unicodedata.normalize("NFC", block)

    # Sửa các lỗi copy-paste nút/href trong block này
    correct_href = f"/dashboard/part-{part_num}/"
    correct_label = f"Mở Part {part_num}"

    block = re.sub(
        r'href=(["\'])/dashboard/part-[1234]/\1',
        rf'href=\1{correct_href}\1',
        block,
    )
    block = re.sub(
        r'href=(["\'])/dashboard/part-[1234]/(["\'])',
        rf'href=\1{correct_href}\2',
        block,
    )
    block = re.sub(
        r'href=(["\'])/part-[1234]/\1',
        rf'href=\1{correct_href}\1',
        block,
    )
    block = re.sub(
        r'href=(["\'])/part-[1234]/(["\'])',
        rf'href=\1{correct_href}\2',
        block,
    )

    block = re.sub(r'Mở Part\s*[1234]', correct_label, block)

    # Sửa thủ công các chuỗi tiếng Việt hay bị tách dấu sau normalize nếu vẫn còn dạng lạ
    replacements = {
        "tiế ́ p": "tiếp",
        "tiế ́p": "tiếp",
        "tiếp": "tiếp",
        "chi tiế ́ t": "chi tiết",
        "chi tiế ́t": "chi tiết",
        "chi tiết": "chi tiết",
        "Có thể tiế ́ p tục": "Có thể tiếp tục",
        "Có thể tiếp tục mở rộng giao diện chi tiế ́ t": "Có thể tiếp tục mở rộng giao diện chi tiết",
    }

    for old, new in replacements.items():
        block = block.replace(old, new)

    return before + block + after

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Chỉ sửa file chọn Part có đủ 4 thẻ
    if not all(part in text for part in ["Part 1", "Part 2", "Part 3", "Part 4"]):
        continue

    # Normalize toàn file trước để sửa unicode tổ hợp chung
    text = unicodedata.normalize("NFC", text)

    # Sửa riêng Part 3 và Part 4
    text = fix_part_block(text, 3, 4)
    text = fix_part_block(text, 4, None)

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

# Tạo report kiểm tra lại
report = Path("part3_part4_fix_report.txt")
lines = ["=== PART 3 / PART 4 FIX REPORT ==="]

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not all(part in text for part in ["Part 1", "Part 2", "Part 3", "Part 4"]):
        continue

    lines.append(f"\nFILE: {path}")

    for part_num in [3, 4]:
        marker = f"Part {part_num}"
        start = text.find(marker)
        if start == -1:
            continue
        end = text.find(f"Part {part_num + 1}", start + len(marker)) if part_num == 3 else len(text)
        if end == -1:
            end = len(text)
        block = text[start:end]

        hrefs = re.findall(r'href=["\']([^"\']+)["\']', block)
        labels = re.findall(r'Mở Part\s*[1234]', block)

        lines.append(f"Part {part_num} labels: {labels}")
        lines.append(f"Part {part_num} hrefs: {hrefs}")
        if "tiế ́" in block or "tiế" in block or "chi tiế ́" in block:
            lines.append(f"WARNING: Part {part_num} may still contain decomposed accents.")

report.write_text("\n".join(lines), encoding="utf-8")

print("Changed files:")
for f in changed:
    print("-", f)

print("Report:", report)
print("Backup:", backup_dir)
print("DONE")
