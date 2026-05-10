from pathlib import Path
import re

# 1) Đảm bảo core/views.py có view admin_student_lookup
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

if "def admin_student_lookup(request):" not in v:
    v += r'''

# ===== Custom admin student lookup/profile page =====
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import StudentProfile

def _is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(_is_admin_user)
def admin_student_lookup(request):
    q = (request.GET.get("q") or request.POST.get("q") or "").strip()
    profile_id = (request.GET.get("profile_id") or request.POST.get("profile_id") or "").strip()

    results = StudentProfile.objects.none()
    selected = None

    if q:
        filters = (
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

        for f in StudentProfile._meta.fields:
            if f.get_internal_type() in ["CharField", "TextField", "EmailField"]:
                filters |= Q(**{f"{f.name}__icontains": q})

        results = StudentProfile.objects.filter(filters).select_related("user").distinct().order_by("-id")[:12]

    if profile_id:
        selected = StudentProfile.objects.filter(id=profile_id).select_related("user").first()
    elif results:
        selected = results.first()

    if request.method == "POST" and request.POST.get("action") == "save_profile":
        selected = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if not selected:
            messages.error(request, "Chưa chọn học viên.")
            return redirect("admin_student_lookup")

        gmail = request.POST.get("gmail", "").strip()
        phone = request.POST.get("phone", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()

        if selected.user:
            selected.user.email = gmail
            selected.user.first_name = full_name
            selected.user.save()

        for field, value in [
            ("email", gmail),
            ("gmail", gmail),
            ("phone", phone),
            ("phone_number", phone),
            ("sdt", phone),
            ("full_name", full_name),
            ("name", full_name),
            ("student_id", student_id),
        ]:
            if hasattr(selected, field):
                setattr(selected, field, value)

        selected.save()
        messages.success(request, "Đã lưu hồ sơ học viên.")
        return redirect(f"{request.path}?profile_id={selected.id}&q={q}")

    def val(obj, names):
        if not obj:
            return ""
        for name in names:
            if hasattr(obj, name):
                return getattr(obj, name) or ""
        return ""

    context = {
        "q": q,
        "results": results,
        "selected": selected,
        "student_id_value": val(selected, ["student_id", "student_code", "code"]),
        "phone_value": val(selected, ["phone", "phone_number", "sdt"]),
        "profile_email_value": val(selected, ["email", "gmail"]),
        "profile_name_value": val(selected, ["full_name", "name"]),
    }

    return render(request, "core/admin_student_lookup.html", context)
# ===== End custom admin student lookup/profile page =====
'''
    views.write_text(v, encoding="utf-8")
    print("DA_THEM_VIEW_admin_student_lookup")
else:
    print("VIEW_admin_student_lookup_DA_CO")


# 2) Đảm bảo core/urls.py có path dashboard/students/
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from django.urls import path" not in u:
    u = "from django.urls import path\n" + u

if "from . import views" not in u:
    u = u.replace("from django.urls import path\n", "from django.urls import path\nfrom . import views\n", 1)

# Xóa dòng dashboard/students cũ nếu có lỗi
u = re.sub(r'\s*path\(["\']dashboard/students/["\'],\s*.*?\),\s*', "\n", u)

# Chèn ngay sau urlpatterns = [
u = re.sub(
    r"urlpatterns\s*=\s*\[",
    'urlpatterns = [\n    path("dashboard/students/", views.admin_student_lookup, name="admin_student_lookup"),',
    u,
    count=1
)

urls.write_text(u, encoding="utf-8")
print("DA_THEM_URL_dashboard_students")


# 3) Tạo template nếu chưa có
tpl = Path("templates/core/admin_student_lookup.html")
tpl.parent.mkdir(parents=True, exist_ok=True)

tpl.write_text(r'''<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Duyệt học viên</title>
<style>
*{box-sizing:border-box}
body{
    margin:0;
    padding:24px;
    background:linear-gradient(135deg,#fffafa,#fff1f4);
    color:#3f0011;
    font-family:Georgia,"Times New Roman",serif;
}
.wrap{
    display:grid;
    grid-template-columns:380px minmax(0,1fr);
    gap:22px;
    max-width:1180px;
    margin:0 auto;
}
.card{
    background:white;
    border:1px solid #ffd1dc;
    border-radius:26px;
    box-shadow:0 18px 42px rgba(180,0,30,.08);
    overflow:hidden;
}
.head{
    padding:18px 22px;
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
}
.head h2{
    margin:0;
    font-size:25px;
    font-weight:950;
}
.head p{
    margin:7px 0 0;
    font-weight:700;
    opacity:.9;
}
.body{padding:22px}
label{
    display:block;
    margin:0 0 7px;
    color:#7a0010;
    font-weight:950;
}
input{
    width:100%;
    height:48px;
    padding:0 15px;
    border-radius:16px;
    border:1px solid #ffd1dc;
    font-size:16px;
    font-family:inherit;
}
input:focus{
    outline:none;
    border-color:#e60023;
    box-shadow:0 0 0 4px rgba(230,0,35,.1);
}
.btn{
    border:0;
    min-height:48px;
    padding:0 20px;
    border-radius:16px;
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
    font-weight:950;
    font-size:16px;
    font-family:inherit;
    cursor:pointer;
}
.form-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:16px;
}
.result-list{
    display:grid;
    gap:10px;
    margin-top:18px;
}
.result-item{
    display:block;
    padding:13px 14px;
    border:1px solid #ffd1dc;
    border-radius:16px;
    background:#fffafa;
    color:#3f0011;
    text-decoration:none;
}
.result-item.active,.result-item:hover{
    background:#fff1f4;
}
.result-name{
    font-size:17px;
    font-weight:950;
    color:#65000e;
}
.result-meta{
    margin-top:4px;
    color:#667085;
    font-size:14px;
    line-height:1.45;
}
.empty{
    padding:28px;
    border:1px dashed #ffb6c2;
    border-radius:20px;
    color:#667085;
    line-height:1.6;
}
.messages{margin-bottom:14px}
.message{
    padding:12px 14px;
    border-radius:14px;
    background:#ecfdf3;
    color:#027a48;
    font-weight:900;
}
.save-row{
    display:flex;
    justify-content:flex-end;
    margin-top:18px;
}
@media(max-width:900px){
    .wrap{grid-template-columns:1fr}
    .form-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">
    <section class="card">
        <div class="head">
            <h2>Tra học viên</h2>
            <p>Nhập tên, Gmail, SĐT hoặc ID học viên.</p>
        </div>
        <div class="body">
            <form method="get">
                <label>Thông tin cần tra</label>
                <input name="q" value="{{ q }}" placeholder="Tên, Gmail, SĐT, ID học viên...">
                <div style="height:12px"></div>
                <button class="btn" type="submit">Tra học viên</button>
            </form>

            <div class="result-list">
                {% for item in results %}
                    <a class="result-item {% if selected and item.id == selected.id %}active{% endif %}"
                       href="?q={{ q|urlencode }}&profile_id={{ item.id }}">
                        <div class="result-name">
                            {% if item.full_name %}{{ item.full_name }}
                            {% elif item.name %}{{ item.name }}
                            {% elif item.user.first_name %}{{ item.user.first_name }}
                            {% else %}{{ item.user.username }}{% endif %}
                        </div>
                        <div class="result-meta">
                            Gmail: {{ item.user.email|default:"Chưa có" }}<br>
                            Tài khoản: {{ item.user.username }}
                        </div>
                    </a>
                {% empty %}
                    {% if q %}<div class="empty">Không tìm thấy học viên phù hợp.</div>{% endif %}
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="card">
        <div class="head">
            <h2>Hồ sơ học viên</h2>
            <p>Cập nhật Gmail, SĐT, tên và ID học viên.</p>
        </div>
        <div class="body">
            {% if messages %}
                <div class="messages">
                    {% for message in messages %}
                        <div class="message">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}

            {% if selected %}
                <form method="post">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="save_profile">
                    <input type="hidden" name="profile_id" value="{{ selected.id }}">
                    <input type="hidden" name="q" value="{{ q }}">

                    <div class="form-grid">
                        <div>
                            <label>Gmail</label>
                            <input name="gmail" value="{% if profile_email_value %}{{ profile_email_value }}{% else %}{{ selected.user.email }}{% endif %}">
                        </div>
                        <div>
                            <label>Số điện thoại</label>
                            <input name="phone" value="{{ phone_value }}">
                        </div>
                        <div>
                            <label>Tên học viên</label>
                            <input name="full_name" value="{% if profile_name_value %}{{ profile_name_value }}{% else %}{{ selected.user.first_name }}{% endif %}">
                        </div>
                        <div>
                            <label>ID học viên</label>
                            <input name="student_id" value="{{ student_id_value }}" placeholder="Bạn tự thêm">
                        </div>
                    </div>

                    <div class="save-row">
                        <button class="btn" type="submit">Lưu hồ sơ học viên</button>
                    </div>
                </form>
            {% else %}
                <div class="empty">
                    Chưa chọn học viên. Hãy tra học viên bên trái trước.
                </div>
            {% endif %}
        </div>
    </section>
</div>
</body>
</html>
''', encoding="utf-8")

print("DA_FIX_FULL_DASHBOARD_STUDENTS")
