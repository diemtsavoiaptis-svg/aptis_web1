from pathlib import Path
import shutil
import re
from datetime import datetime

print("=== RESTORE CONTENT AND REMOVE ONLY LESSON MENU/CARD ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_now = Path("code_backups") / f"before_restore_lesson_fix_{stamp}"
backup_now.mkdir(parents=True, exist_ok=True)

# 1) Gỡ file CSS/JS ẩn quá rộng
for bad in [
    Path("static/css/hide_lessons_items.css"),
    Path("static/js/hide_lessons_items.js"),
]:
    if bad.exists():
        shutil.copy2(bad, backup_now / bad.name)
        bad.unlink()
        print("Deleted broad hide file:", bad)

# 2) Gỡ link CSS/JS ẩn lesson khỏi tất cả template
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    text = re.sub(r'\s*<link[^>]+hide_lessons_items\.css[^>]*>\s*', "\n", text)
    text = re.sub(r'\s*<script[^>]+hide_lessons_items\.js[^>]*></script>\s*', "\n", text)

    if text != original:
        shutil.copy2(path, backup_now / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Removed broad hide references:", path)

# 3) Khôi phục template từ backup trước khi ẩn lesson nếu có
backup_dirs = sorted(Path("code_backups").glob("before_hide_lesson_items_*"))
if backup_dirs:
    latest = backup_dirs[-1]
    print("Restoring templates from:", latest)

    for backup_file in latest.iterdir():
        if not backup_file.is_file():
            continue
        original_path = Path(backup_file.name.replace("__", "/"))
        if original_path.suffix.lower() == ".html":
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, original_path)
            print("Restored:", original_path)
else:
    print("No before_hide_lesson_items backup found. Continuing with cleanup only.")

# 4) Xoá CHỈ link/menu có chữ Quản lý bài học
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Quản lý bài học" not in text:
        continue

    shutil.copy2(path, backup_now / ("lesson_exact__" + str(path).replace("\\", "__").replace("/", "__")))

    # Xoá đúng thẻ <a> menu chứa Quản lý bài học
    text = re.sub(
        r'(?is)\s*<a\b[^>]*>.*?Quản lý bài học.*?</a>\s*',
        "\n",
        text,
        count=1
    )

    # Xoá đúng card dashboard nhỏ chứa Quản lý bài học, chỉ nếu nó là div/card/article độc lập
    text = re.sub(
        r'(?is)\s*<(div|article)\b[^>]*(?:card|tile|panel|item)[^>]*>.*?Quản lý bài học.*?</\1>\s*',
        "\n",
        text,
        count=1
    )

    text = re.sub(r'(?is)<li[^>]*>\s*</li>', '', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("Removed only lesson item from:", path)

print("DONE")
print("Backup saved:", backup_now)
