from pathlib import Path
import re

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
    r'@login_required\s+def dashboard\(request\):.*?return render\(request,\s*"core/dashboard\.html",\s*\{\s*"lessons":\s*lessons\s*\}\)',
    new_dashboard.rstrip(),
    text,
    count=1,
    flags=re.S
)

p.write_text(text2, encoding="utf-8")
print("DA_SUA_DASHBOARD" if count else "CHUA_TIM_THAY_DASHBOARD")
