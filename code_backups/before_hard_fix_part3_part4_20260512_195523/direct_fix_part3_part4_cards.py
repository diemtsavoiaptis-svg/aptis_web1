from pathlib import Path
import shutil
import unicodedata
from datetime import datetime

print("=== DIRECT FIX VISIBLE PART 3 / PART 4 CARD ERRORS ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_direct_fix_part3_part4_cards_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Khu vực quản lý dữ liệu cho Part 3" not in text and "Khu vực quản lý dữ liệu cho Part 4" not in text:
        continue

    shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))

    # Chuẩn hoá Unicode dựng sẵn
    text = unicodedata.normalize("NFC", text)

    # Sửa lỗi dấu bị tách nhìn thấy trên màn
    bad_good = {
        "tiế ́ p": "tiếp",
        "tiế ́p": "tiếp",
        "tiếp": "tiếp",
        "chi tiế ́ t": "chi tiết",
        "chi tiế ́t": "chi tiết",
        "chi tiết": "chi tiết",
        "Có thể tiế ́ p": "Có thể tiếp",
        "giao diện chi tiế ́ t": "giao diện chi tiết",
        "Có thể tiế p": "Có thể tiếp",
        "chi tiế t": "chi tiết",
    }

    for bad, good in bad_good.items():
        text = text.replace(bad, good)

    # Tách theo Part 3 / Part 4 để sửa đúng từng thẻ
    p3 = text.find("Part 3")
    p4 = text.find("Part 4")

    if p3 != -1 and p4 != -1 and p3 < p4:
        before_p3 = text[:p3]
        block3 = text[p3:p4]
        block4 = text[p4:]

        # Trong block Part 3: mọi nút/link mở Part đều phải về Part 3
        block3 = block3.replace("Mở Part 1", "Mở Part 3")
        block3 = block3.replace("Mở Part 2", "Mở Part 3")
        block3 = block3.replace("Mở Part 4", "Mở Part 3")
        block3 = block3.replace('/dashboard/part-1/', '/dashboard/part-3/')
        block3 = block3.replace('/dashboard/part-2/', '/dashboard/part-3/')
        block3 = block3.replace('/dashboard/part-4/', '/dashboard/part-3/')
        block3 = block3.replace('/part-1/', '/dashboard/part-3/')
        block3 = block3.replace('/part-2/', '/dashboard/part-3/')
        block3 = block3.replace('/part-4/', '/dashboard/part-3/')

        # Trong block Part 4: mọi nút/link mở Part đều phải về Part 4
        block4 = block4.replace("Mở Part 1", "Mở Part 4")
        block4 = block4.replace("Mở Part 2", "Mở Part 4")
        block4 = block4.replace("Mở Part 3", "Mở Part 4")
        block4 = block4.replace('/dashboard/part-1/', '/dashboard/part-4/')
        block4 = block4.replace('/dashboard/part-2/', '/dashboard/part-4/')
        block4 = block4.replace('/dashboard/part-3/', '/dashboard/part-4/')
        block4 = block4.replace('/part-1/', '/dashboard/part-4/')
        block4 = block4.replace('/part-2/', '/dashboard/part-4/')
        block4 = block4.replace('/part-3/', '/dashboard/part-4/')

        text = before_p3 + block3 + block4

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("Changed files:")
for f in changed:
    print("-", f)

print("Backup:", backup_dir)
print("DONE")
