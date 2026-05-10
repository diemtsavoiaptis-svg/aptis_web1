from pathlib import Path
import re

p = Path("core/views.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Thêm import csrf_exempt nếu chưa có
if "from django.views.decorators.csrf import csrf_exempt" not in s:
    s = "from django.views.decorators.csrf import csrf_exempt\n" + s

# Xóa csrf_exempt lặp nếu có
s = re.sub(r"(?m)^@csrf_exempt\s*\n(?=@csrf_exempt)", "", s)

# Đảm bảo view admin_student_lookup có @csrf_exempt ngay phía trên
s = re.sub(
    r"(?m)^(@user_passes_test\(_is_admin_user\)\s*\ndef admin_student_lookup\(request\):)",
    "@csrf_exempt\n\\1",
    s,
    count=1
)

# Nếu view không có user_passes_test thì gắn trực tiếp trước def
if "@csrf_exempt\ndef admin_student_lookup" not in s and "@csrf_exempt\n@user_passes_test(_is_admin_user)\ndef admin_student_lookup" not in s:
    s = re.sub(
        r"(?m)^def admin_student_lookup\(request\):",
        "@csrf_exempt\ndef admin_student_lookup(request):",
        s,
        count=1
    )

p.write_text(s, encoding="utf-8")
print("DA_FIX_CSRF_LUU_HO_SO_LOCAL")
