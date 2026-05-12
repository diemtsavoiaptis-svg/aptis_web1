from pathlib import Path
import shutil
import re
from datetime import datetime

print("=== RESTORE DASHBOARD CONTENT SAFE ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_now = Path("code_backups") / f"before_restore_all_dashboard_{stamp}"
backup_now.mkdir(parents=True, exist_ok=True)

# Backup hiện trạng đang lỗi
for folder in ["templates", "static", "core"]:
    p = Path(folder)
    if p.exists():
        dest = backup_now / folder
        shutil.copytree(p, dest, dirs_exist_ok=True)

# 1) Xoá các file ẩn quá rộng đã tạo trước đó
bad_files = [
    Path("static/css/hide_lessons_items.css"),
    Path("static/js/hide_lessons_items.js"),
    Path("static/css/sidebar_compact_fix.css"),
]

for f in bad_files:
    if f.exists():
        f.unlink()
        print("Deleted bad injected file:", f)

# 2) Gỡ mọi dòng nạp CSS/JS gây ẩn dữ liệu
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    text = re.sub(r'\s*<link[^>]+hide_lessons_items\.css[^>]*>\s*', "\n", text)
    text = re.sub(r'\s*<script[^>]+hide_lessons_items\.js[^>]*></script>\s*', "\n", text)
    text = re.sub(r'\s*<link[^>]+sidebar_compact_fix\.css[^>]*>\s*', "\n", text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("Cleaned injected refs:", path)

print("DONE CLEANUP")
print("Backup current broken state saved at:", backup_now)
