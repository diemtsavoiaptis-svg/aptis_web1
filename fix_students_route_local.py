from pathlib import Path
import re

# =========================
# 1) Đảm bảo core/urls.py có route dashboard/students/
# =========================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from django.urls import path" not in u:
    u = "from django.urls import path\n" + u

if "from . import views" not in u:
    u = u.replace("from django.urls import path\n", "from django.urls import path\nfrom . import views\n", 1)

# Delete route cũ nếu bị lỗi/lặp
u = re.sub(
    r'\s*path\(["\']dashboard/students/["\'],\s*.*?\),\s*',
    "\n",
    u
)

# Add route mới ngay đầu urlpatterns
u = re.sub(
    r"urlpatterns\s*=\s*\[",
    'urlpatterns = [\n    path("dashboard/students/", views.admin_student_lookup, name="admin_student_lookup"),',
    u,
    count=1
)

urls.write_text(u, encoding="utf-8")


# =========================
# 2) Đảm bảo dashboard button trỏ đúng link mới
# =========================
dash = Path("templates/core/dashboard.html")
if dash.exists():
    d = dash.read_text(encoding="utf-8", errors="ignore")
    d = d.replace('data-url="/admin/core/studentprofile/"', 'data-url="/dashboard/students/"')
    d = d.replace('href="/admin/core/studentprofile/"', 'href="/dashboard/students/"')
    dash.write_text(d, encoding="utf-8")


# =========================
# 3) Kiểm tra view tồn tại
# =========================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

if "def admin_student_lookup(request):" not in v:
    raise SystemExit("LOI: core/views.py chua co view admin_student_lookup")

print("DA_SUA_LOCAL_ROUTE_DASHBOARD_STUDENTS")
