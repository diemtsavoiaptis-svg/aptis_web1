from pathlib import Path
import shutil
from datetime import datetime

target = "Khu vực quản lý dữ liệu cho Part 2. Có thể tiếp tục mở rộng giao diện chi tiết sau khi hoàn thiện Part 1."

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_remove_part2_description_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if target in text:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        text = text.replace(target, "")
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Removed from:")
for f in changed:
    print("-", f)

print("Backup:", backup_dir)
print("DONE")
