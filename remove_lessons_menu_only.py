from pathlib import Path
import re
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_remove_lessons_menu_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

targets = [p for p in Path("templates").rglob("*.html")]

removed = []

for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Quản lý bài học" not in text:
        continue

    shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))

    # Xoá đúng 1 thẻ <a> chứa chữ "Quản lý bài học"
    text = re.sub(
        r'(?is)\s*<a\b[^>]*>.*?Quản lý bài học.*?</a>\s*',
        "\n",
        text,
        count=1
    )

    # Xoá wrapper rỗng nếu có
    text = re.sub(r'(?is)<li[^>]*>\s*</li>', '', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        removed.append(str(path))

print("Removed 'Quản lý bài học' from:")
for item in removed:
    print("-", item)

print("Backup:", backup_dir)
