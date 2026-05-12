from pathlib import Path
import re
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_fix_only_part3_button_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for path in list(Path("templates").rglob("*.html")) + list(Path("core").rglob("*.py")) + list(Path("static").rglob("*.js")):
    if not path.is_file():
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Part 3" not in text or "Mở Part 2" not in text:
        continue

    # Chỉ lấy vùng từ Part 3 đến Part 4, sửa trong vùng đó thôi
    p3 = text.find("Part 3")
    p4 = text.find("Part 4", p3)

    if p3 != -1:
        if p4 == -1:
            before = text[:p3]
            block = text[p3:]
            after = ""
        else:
            before = text[:p3]
            block = text[p3:p4]
            after = text[p4:]

        block = block.replace("Mở Part 2", "Mở Part 3")
        block = block.replace('/dashboard/part-2/', '/dashboard/part-3/')
        block = block.replace('"dashboard/part-2/"', '"dashboard/part-3/"')
        block = block.replace("'dashboard/part-2/'", "'dashboard/part-3/'")

        text = before + block + after

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Fixed files:")
for item in changed:
    print("-", item)

print("Backup:", backup_dir)
print("DONE: only Part 3 button fixed.")
