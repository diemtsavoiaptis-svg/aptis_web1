from pathlib import Path
import re

p = Path("core/models.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Tìm class Part2Topic
m = re.search(r"class\s+Part2Topic\(models\.Model\):\s*\n", s)

if not m:
    raise SystemExit("KHONG_TIM_THAY_CLASS_Part2Topic")

# Nếu chưa có VERSION_CHOICES thì thêm ngay đầu class
topic_block = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s).group(0)

insert = '''    VERSION_CHOICES = [
        ("gioi", "Mày giỏi"),
        ("kem", "Mày kém"),
    ]

    version = models.CharField("Phiên bản", max_length=20, choices=VERSION_CHOICES, default="gioi")
'''

if "version = models.CharField" not in topic_block:
    s = s[:m.end()] + insert + s[m.end():]
    print("DA_THEM_FIELD_VERSION_CHO_Part2Topic")
else:
    print("FIELD_VERSION_DA_CO_SAN")

p.write_text(s, encoding="utf-8")
