from pathlib import Path
import re

# =========================
# 1) Đảm bảo StudentProfile có đủ field hồ sơ
# =========================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

needed_fields = {
    "student_id": "    student_id = models.CharField('ID học viên', max_length=80, blank=True)\n",
    "full_name": "    full_name = models.CharField('Tên học viên', max_length=150, blank=True)\n",
    "phone": "    phone = models.CharField('Số điện thoại', max_length=30, blank=True)\n",
    "email": "    email = models.EmailField('Gmail', blank=True)\n",
}

insert_text = ""
for field, line in needed_fields.items():
    if re.search(rf"^\s*{field}\s*=", s, flags=re.M) is None:
        insert_text += line

if insert_text:
    s = re.sub(
        r"(class\s+StudentProfile\s*\(\s*models\.Model\s*\)\s*:\s*\n)",
        r"\1" + insert_text,
        s,
        count=1
    )

models.write_text(s, encoding="utf-8")


# =========================
# 2) Ghi đè view lưu hồ sơ học viên cho chắc
# =========================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.views.decorators.csrf import csrf_exempt",
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.contrib import messages",
    "from django.db.models import Q",
    "from django.shortcuts import render, redirect",
    "from .models import StudentProfile",
]

for imp in imports:
    if imp not in v:
        v = imp + "\n" + v

# Xóa các bản admin_student_lookup cũ nếu có
v = re.sub(
    r"\n?# ===== Custom admin student lookup/profile page =====[\s\S]*?# ===== End custom admin student lookup/profile page =====\n?",
    "\n",
    v
)

v = re.sub(
    r"(?ms)^@csrf_exempt\s*\n@user_passes_test\(_is_admin_user\)\s*\ndef admin_student_lookup\(request\):[\s\S]*?(?=\n#|\n@|\ndef |\Z)",
    "\n",
    v
)

v = re.sub(
    r"(?ms)^@user_passes_test\(_is_admin_user\)\s*\ndef admin_student_lookup\(request\):[\s\S]*?(?=\n#|\n@|\ndef |\Z)",
    "\n",
    v
)

v += r'''

# ===== Custom admin student lookup/profile page =====
def _is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@csrf_exempt
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
            Q(user__last_name__icontains=q) |
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(student_id__icontains=q)
        )

        if q.isdigit():
            filters |= Q(id=int(q)) | Q(user__id=int(q))

        results = StudentProfile.objects.filter(filters).select_related("user").distinct().order_by("-id")[:20]

    if profile_id:
        selected = StudentProfile.objects.filter(id=profile_id).select_related("user").first()
    elif results:
        selected = results.first()

    if request.method == "POST" and request.POST.get("action") == "save_profile":
        selected = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if not selected:
            messages.error(request, "Chưa chọn học viên để lưu.")
            return redirect("admin_student_lookup")

        gmail = request.POST.get("gmail", "").strip()
        phone = request.POST.get("phone", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()

        selected.email = gmail
        selected.phone = phone
        selected.full_name = full_name
        selected.student_id = student_id
        selected.save()

        if selected.user:
            selected.user.email = gmail
            selected.user.first_name = full_name
            selected.user.save()

        messages.success(request, "Đã lưu hồ sơ học viên.")
        return redirect(f"{request.path}?profile_id={selected.id}&q={gmail or phone or full_name or student_id or q}")

    if request.method == "POST" and request.POST.get("action") == "delete_profile":
        target = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if target:
            target.email = ""
            target.phone = ""
            target.full_name = ""
            target.student_id = ""
            target.save()

            if target.user:
                target.user.email = ""
                target.user.first_name = ""
                target.user.last_name = ""
                target.user.save()

            messages.success(request, "Đã xóa thông tin hồ sơ học viên.")

        return redirect("admin_student_lookup")

    saved_profiles = StudentProfile.objects.select_related("user").all().order_by("-id")

    return render(request, "core/admin_student_lookup.html", {
        "q": q,
        "results": results,
        "selected": selected,
        "saved_profiles": saved_profiles,
        "student_id_value": selected.student_id if selected else "",
        "phone_value": selected.phone if selected else "",
        "profile_email_value": selected.email if selected else "",
        "profile_name_value": selected.full_name if selected else "",
    })
# ===== End custom admin student lookup/profile page =====
'''

views.write_text(v, encoding="utf-8")


# =========================
# 3) Sửa template để value lấy đúng field đã lưu
# =========================
tpl = Path("templates/core/admin_student_lookup.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

t = re.sub(
    r'<input name="gmail"[^>]*>',
    '<input name="gmail" value="{{ profile_email_value }}" placeholder="Gmail học viên">',
    t
)

t = re.sub(
    r'<input name="phone"[^>]*>',
    '<input name="phone" value="{{ phone_value }}" placeholder="Số điện thoại">',
    t
)

t = re.sub(
    r'<input name="full_name"[^>]*>',
    '<input name="full_name" value="{{ profile_name_value }}" placeholder="Tên học viên">',
    t
)

t = re.sub(
    r'<input name="student_id"[^>]*>',
    '<input name="student_id" value="{{ student_id_value }}" placeholder="ID học viên tự thêm">',
    t
)

tpl.write_text(t, encoding="utf-8")

print("DA_FIX_LUU_HO_SO_HOC_VIEN_CHAC_CHAN")
