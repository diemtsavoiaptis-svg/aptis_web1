from pathlib import Path
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_rename_part3_button_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Part 3" not in text:
        continue

    # Chỉ sửa trong vùng Part 3, không đụng Part 1/2/4
    p3 = text.find("Part 3")
    p4 = text.find("Part 4", p3)

    if p3 == -1:
        continue

    before = text[:p3]
    block = text[p3:p4 if p4 != -1 else len(text)]
    after = text[p4:] if p4 != -1 else ""

    block = block.replace("Mở Part 3", "Mở dữ liệu Part 3")
    block = block.replace("Mở Part 2", "Mở dữ liệu Part 3")  # nếu Part 3 vẫn còn bị sai label cũ

    # Đảm bảo link Part 3 vẫn mở đúng trang Part 3
    block = block.replace('/dashboard/part-2/', '/dashboard/part-3/')
    block = block.replace('/dashboard/part-1/', '/dashboard/part-3/')
    block = block.replace('/dashboard/part-4/', '/dashboard/part-3/')

    text = before + block + after

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Changed files:")
for f in changed:
    print("-", f)

print("Backup:", backup_dir)
print("DONE")
