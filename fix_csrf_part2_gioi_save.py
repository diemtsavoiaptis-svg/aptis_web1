from pathlib import Path
import re

# ==================================================
# 1) Add csrf_exempt import vào views.py
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

if "from django.views.decorators.csrf import csrf_exempt" not in s:
    s = "from django.views.decorators.csrf import csrf_exempt\n" + s

# ==================================================
# 2) Gắn csrf_exempt cho view admin_part2_gioi_detail
#    để nút Save answer tổng / Save answer đúng không bị Origin null
# ==================================================
s = re.sub(
    r'(@user_passes_test\([^)]+\)\s*\ndef admin_part2_gioi_detail\(request, topic_id\):)',
    r'@csrf_exempt\n\1',
    s
)

# Tránh bị lặp csrf_exempt nhiều lần
s = re.sub(
    r'(@csrf_exempt\s*\n)+(@user_passes_test\([^)]+\)\s*\ndef admin_part2_gioi_detail)',
    r'@csrf_exempt\n\2',
    s
)

views.write_text(s, encoding="utf-8")


# ==================================================
# 3) Add trusted origins local/online vào settings.py cho chắc
# ==================================================
settings = Path("config/settings.py")
t = settings.read_text(encoding="utf-8", errors="ignore")

if "CSRF_TRUSTED_ORIGINS" not in t:
    t += r'''

# CSRF trusted origins for local + PythonAnywhere
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://diemtsavoiaptis.pythonanywhere.com",
    "https://diemtsavoiaptis.pythonanywhere.com",
]
'''
else:
    # Bổ sung nếu thiếu
    for origin in [
        '"http://127.0.0.1:8000"',
        '"http://localhost:8000"',
        '"http://diemtsavoiaptis.pythonanywhere.com"',
        '"https://diemtsavoiaptis.pythonanywhere.com"',
    ]:
        if origin not in t:
            t = t.replace("CSRF_TRUSTED_ORIGINS = [", f"CSRF_TRUSTED_ORIGINS = [\n    {origin},", 1)

settings.write_text(t, encoding="utf-8")

print("DA_SUA_LOI_CSRF_CHO_LUU_DAP_AN_TONG_MAY_GIOI")
