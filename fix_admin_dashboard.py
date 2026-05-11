from pathlib import Path
import re

# 1) Ép user admin thành staff/superuser/is_active
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth.models import User

u, created = User.objects.get_or_create(username="admin")
u.email = "admin@gmail.com"
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.set_password("hoangtong214")
u.save()

# Nếu có user admin@gmail.com separate thì cũng set luôn
for x in User.objects.filter(username="admin@gmail.com"):
    x.is_staff = True
    x.is_superuser = True
    x.is_active = True
    x.set_password("hoangtong214")
    x.save()

print("ADMIN_READY:", u.username, u.email, u.is_staff, u.is_superuser, u.is_active)


# 2) Edit dashboard: admin/admin@gmail.com chắc chắn vào dashboard admin
p = Path("core/views.py")
text = p.read_text(encoding="utf-8", errors="ignore")

new_dashboard = '''@login_required
def dashboard(request):
    lessons = Lesson.objects.all().order_by("-created_at")

    is_admin_user = (
        request.user.is_staff
        or request.user.is_superuser
        or request.user.username == "admin"
        or request.user.email == "admin@gmail.com"
    )

    if is_admin_user:
        return render(request, "core/dashboard.html", {
            "lessons": lessons
        })

    return redirect("listening")
'''

text2, count = re.subn(
    r'@login_required\s+def dashboard\(request\):.*?return redirect\("listening"\)\n',
    new_dashboard + "\n",
    text,
    count=1,
    flags=re.S
)

if count == 0:
    print("CHUA_TIM_THAY_DASHBOARD_DE_SUA")
else:
    p.write_text(text2, encoding="utf-8")
    print("DA_SUA_DASHBOARD_ADMIN_CHAC_CHAN")
