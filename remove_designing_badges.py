from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== REMOVE ALL DESIGNING BADGES / FOCUS SCRIPTS ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_remove_designing_badges_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Xoá các file CSS/JS tạo chữ "Đang thiết kế"
bad_files = [
    Path("static/css/focus_part2_only.css"),
    Path("static/js/focus_part2_only.js"),
    Path("static/css/focus_part3_only.css"),
    Path("static/js/focus_part3_only.js"),
]

for f in bad_files:
    if f.exists():
        shutil.copy2(f, backup_dir / f.name)
        f.unlink()
        print("Deleted:", f)

# 2) Gỡ link/script focus khỏi toàn bộ template
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    text = re.sub(r'\s*<link[^>]+focus_part2_only\.css[^>]*>\s*', "\n", text)
    text = re.sub(r'\s*<script[^>]+focus_part2_only\.js[^>]*></script>\s*', "\n", text)
    text = re.sub(r'\s*<link[^>]+focus_part3_only\.css[^>]*>\s*', "\n", text)
    text = re.sub(r'\s*<script[^>]+focus_part3_only\.js[^>]*></script>\s*', "\n", text)

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Cleaned:", path)

print("DONE. Removed all 'Đang thiết kế' focus effects.")
print("Backup:", backup_dir)
