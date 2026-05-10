from pathlib import Path
import re

p = Path("core/views.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Thêm import csrf_exempt nếu chưa có
if "from django.views.decorators.csrf import csrf_exempt" not in s:
    s = "from django.views.decorators.csrf import csrf_exempt\n" + s

# Thêm @csrf_exempt ngay trước view admin_student_lookup
s = re.sub(
    r"(@user_passes_test\(_is_admin_user\)\s*\ndef admin_student_lookup\(request\):)",
    "@csrf_exempt\n\\1",
    s,
    count=1
)

# Nếu bị lặp nhiều @csrf_exempt thì gọn lại
s = re.sub(r"(@csrf_exempt\s*){2,}", "@csrf_exempt\n", s)

p.write_text(s, encoding="utf-8")
print("DA_SUA_CSRF_LUU_HO_SO_HOC_VIEN")
