from pathlib import Path
import re

p = Path("core/urls.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Đảm bảo có import views
if "from . import views" not in s:
    s = "from . import views\n" + s

# Add URL dashboard/students nếu chưa có
if 'dashboard/students/' not in s:
    s = re.sub(
        r"urlpatterns\s*=\s*\[",
        'urlpatterns = [\n    path("dashboard/students/", views.admin_student_lookup, name="admin_student_lookup"),',
        s,
        count=1
    )

p.write_text(s, encoding="utf-8")
print("DA_THEM_URL_DUYET_HOC_VIEN")
