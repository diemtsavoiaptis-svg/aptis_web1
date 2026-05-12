from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== REMOVE ONLY LESSON MANAGEMENT UI ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_remove_lesson_management_ui_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Backup toàn bộ template trước khi sửa
for folder in ["templates", "core"]:
    p = Path(folder)
    if p.exists():
        shutil.copytree(p, backup_dir / folder, dirs_exist_ok=True)

# 2) Xoá nút/menu/card có chữ "Quản lý bài học" khỏi dashboard/sidebar
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Quản lý bài học" in text:
        # Xoá link menu/sidebar chứa Quản lý bài học
        text = re.sub(
            r'(?is)\s*<a\b[^>]*>.*?Quản lý bài học.*?</a>\s*',
            "\n",
            text
        )

        # Xoá button chứa Quản lý bài học
        text = re.sub(
            r'(?is)\s*<button\b[^>]*>.*?Quản lý bài học.*?</button>\s*',
            "\n",
            text
        )

        # Xoá card/block dashboard chứa Quản lý bài học
        text = re.sub(
            r'(?is)\s*<(div|article|section)\b[^>]*(?:card|tile|panel|item|box)[^>]*>.*?Quản lý bài học.*?</\1>\s*',
            "\n",
            text
        )

        # Xoá li rỗng nếu có
        text = re.sub(r'(?is)<li[^>]*>\s*</li>', '', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("Removed lesson menu/card from:", path)

# 3) Xoá nội dung trang quản lý bài học nếu file đó tồn tại
lesson_markers = [
    "Chọn Bài học để thay đổi",
    "Tiêu đề bài học",
    "Thêm, sửa và quản lý bài học",
    "Bài 1 - Giới thiệu Aptis",
]

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")

    if any(marker in text for marker in lesson_markers):
        print("Clearing lesson page content:", path)

        # Nếu là template có extends thì giữ extends/block, chỉ để trống content
        if "{% block" in text and "{% endblock" in text:
            # Thử giữ nguyên cấu trúc template nhưng làm rỗng phần body/content
            text = re.sub(
                r'(?is){% block content %}.*?{% endblock %}',
                '{% block content %}\n{% endblock %}',
                text
            )
            text = re.sub(
                r'(?is){% block main %}.*?{% endblock %}',
                '{% block main %}\n{% endblock %}',
                text
            )
            text = re.sub(
                r'(?is){% block body %}.*?{% endblock %}',
                '{% block body %}\n{% endblock %}',
                text
            )
        else:
            # Nếu là file HTML độc lập thì thay bằng trang trống
            text = """{% load static %}
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title></title>
</head>
<body>
</body>
</html>
"""

        path.write_text(text, encoding="utf-8")

# 4) Xoá dữ liệu Lesson trong database local để bảng không còn hiện bài cũ
# Chỉ chạy nếu Django import được
try:
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from core.models import Lesson
    count = Lesson.objects.count()
    Lesson.objects.all().delete()
    print(f"Deleted {count} Lesson rows from local database.")
except Exception as e:
    print("Skip deleting Lesson rows:", e)

print("DONE")
print("Backup saved at:", backup_dir)
