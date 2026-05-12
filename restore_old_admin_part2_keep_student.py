from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== KEEP STUDENT PART 2 UI, RESTORE OLD ADMIN PART 2 UI ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_restore_old_admin_part2_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# Backup hiện trạng trước khi sửa
for folder in ["templates", "static"]:
    p = Path(folder)
    if p.exists():
        shutil.copytree(p, backup_dir / folder, dirs_exist_ok=True)

# Chỉ gỡ CSS/JS redesign khỏi các template ADMIN Part 2
admin_markers = [
    "Thiết lập Part 2",
    "LƯU DỮ LIỆU",
    "Lưu dữ liệu",
    "Nguồn âm thanh",
    "Danh sách Lựa chọn",
    "Đáp án 4 Speakers",
    "admin_part2",
]

changed = []

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    low_path = str(path).lower()

    is_admin_part2 = (
        "admin_part2" in low_path
        or "dashboard/part-2" in text
        or any(marker in text for marker in admin_markers)
    )

    # Không đụng template học viên
    is_student_template = (
        "student" in low_path
        or "listening_part2" in low_path
        or "student_part2" in low_path
    )

    if not is_admin_part2 or is_student_template:
        continue

    original = text

    # Gỡ file design mới khỏi admin Part 2
    text = re.sub(r'\s*<link[^>]+part2_design_system\.css[^>]*>\s*', "\n", text)
    text = re.sub(r'\s*<script[^>]+part2_design_system\.js[^>]*></script>\s*', "\n", text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Admin Part 2 templates restored to old UI:")
for item in changed:
    print("-", item)

# Ghi chú khóa
lock_note = Path("code_backups") / "LOCKED_UI_NOTES.txt"
lock_note.write_text(
    "LOCKED UI NOTES\n"
    f"Time: {datetime.now()}\n"
    "- Student Part 2 UI: approved and kept.\n"
    "- Admin Part 2 UI: restored/kept as previous existing admin interface.\n"
    "- Future edits should not change Student Part 2 unless user explicitly asks.\n",
    encoding="utf-8"
)

print("DONE")
print("Backup:", backup_dir)
print("Lock note:", lock_note)
