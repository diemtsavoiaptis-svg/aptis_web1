from pathlib import Path
import re

# =========================
# 1) Edit view: thêm xử lý xóa hồ sơ student
# =========================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

delete_block = r'''
    if request.method == "POST" and request.POST.get("action") == "delete_profile":
        target = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if not target:
            messages.error(request, "Không tìm thấy hồ sơ cần xóa.")
            return redirect("admin_student_lookup")

        # Delete information account liên kết nhưng KHÔNG xóa user đăng nhập
        if getattr(target, "user", None):
            target.user.email = ""
            target.user.first_name = ""
            target.user.last_name = ""
            target.user.save()

        # Delete các field information thường dùng trong StudentProfile nếu có
        fields_to_clear = [
            "student_id", "student_code", "code",
            "full_name", "name", "student_name", "ho_ten", "display_name",
            "email", "gmail",
            "phone", "phone_number", "mobile", "sdt", "so_dien_thoai",
        ]

        for field in fields_to_clear:
            if hasattr(target, field):
                setattr(target, field, "")

        target.save()
        messages.success(request, "Đã xóa information hồ sơ student.")
        return redirect("admin_student_lookup")
'''

if 'request.POST.get("action") == "delete_profile"' not in s:
    marker = '    if request.method == "POST" and request.POST.get("action") == "save_profile":'
    s = s.replace(marker, delete_block + "\n" + marker, 1)

views.write_text(s, encoding="utf-8")


# =========================
# 2) Edit template: thêm nút Delete hồ sơ trong bảng đã lưu
# =========================
tpl = Path("templates/core/admin_student_lookup.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# CSS cho nút xóa
css = r'''
.delete-action{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-height:34px;
    padding:0 12px;
    border-radius:999px;
    background:#fff1f4;
    color:#b8001c;
    border:1px solid #ffb6c2;
    font-weight:950;
    font-family:inherit;
    cursor:pointer;
}
.delete-action:hover{
    background:#ffe1e7;
}
.action-row{
    display:flex;
    gap:8px;
    align-items:center;
    flex-wrap:wrap;
}
.inline-delete-form{
    display:inline;
    margin:0;
}
'''

if ".delete-action" not in t:
    t = t.replace("</style>", css + "\n</style>")

# Đổi tiêu đề cột thao tác nếu cần giữ nguyên cũng được
old_action = r'''<td>
                                <a class="saved-action" href="?profile_id={{ item.id }}&q={{ item.user.email|urlencode }}">
                                    Mở hồ sơ
                                </a>
                            </td>'''

new_action = r'''<td>
                                <div class="action-row">
                                    <a class="saved-action" href="?profile_id={{ item.id }}&q={{ item.user.email|urlencode }}">
                                        Mở hồ sơ
                                    </a>

                                    <form class="inline-delete-form" method="post" onsubmit="return confirm('Bạn chắc chắn muốn xóa information hồ sơ student nàyAccount đăng nhập vẫn được giữ lại.');">
                                        {% csrf_token %}
                                        <input type="hidden" name="action" value="delete_profile">
                                        <input type="hidden" name="profile_id" value="{{ item.id }}">
                                        <button class="delete-action" type="submit">Delete hồ sơ</button>
                                    </form>
                                </div>
                            </td>'''

if "delete_profile" not in t:
    if old_action in t:
        t = t.replace(old_action, new_action)
    else:
        t = t.replace(
            '<a class="saved-action" href="?profile_id={{ item.id }}&q={{ item.user.email|urlencode }}">',
            '''<div class="action-row">
                                    <a class="saved-action" href="?profile_id={{ item.id }}&q={{ item.user.email|urlencode }}">''',
            1
        )

tpl.write_text(t, encoding="utf-8")

print("DA_THEM_NUT_XOA_HO_SO_HOC_VIEN")
