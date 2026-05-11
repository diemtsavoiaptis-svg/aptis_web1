from pathlib import Path
import re

# =========================
# 1) Edit view: gửi danh sách hồ sơ đã lưu xuống template
# =========================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

old = '''context = {
        "q": q,
        "results": results,
        "selected": selected,
        "student_id_value": val(selected, ["student_id", "student_code", "code"]),
        "phone_value": val(selected, ["phone", "phone_number", "sdt"]),
        "profile_email_value": val(selected, ["email", "gmail"]),
        "profile_name_value": val(selected, ["full_name", "name"]),
    }'''

new = '''# Danh sách hồ sơ đã lưu để hiển thị bên dưới
    saved_profiles = StudentProfile.objects.select_related("user").all().order_by("-id")

    context = {
        "q": q,
        "results": results,
        "selected": selected,
        "saved_profiles": saved_profiles,
        "student_id_value": val(selected, ["student_id", "student_code", "code"]),
        "phone_value": val(selected, ["phone", "phone_number", "sdt"]),
        "profile_email_value": val(selected, ["email", "gmail"]),
        "profile_name_value": val(selected, ["full_name", "name"]),
    }'''

if old in s:
    s = s.replace(old, new)
elif '"saved_profiles": saved_profiles' not in s:
    s = s.replace(
        '"results": results,',
        '"results": results,\n        "saved_profiles": StudentProfile.objects.select_related("user").all().order_by("-id"),'
    )

views.write_text(s, encoding="utf-8")


# =========================
# 2) Edit template: thêm bảng Hồ sơ đã lưu bên dưới
# =========================
tpl = Path("templates/core/admin_student_lookup.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# Add CSS bảng đẹp
css = r'''
.saved-section{
    margin-top:24px;
}
.saved-table-wrap{
    overflow:auto;
    border-radius:22px;
    border:1px solid #ffd1dc;
    background:white;
}
.saved-table{
    width:100%;
    border-collapse:collapse;
    min-width:760px;
}
.saved-table th{
    background:#fff1f4;
    color:#7a0010;
    font-weight:950;
    padding:14px 12px;
    text-align:left;
    border-bottom:1px solid #ffd1dc;
}
.saved-table td{
    padding:13px 12px;
    border-bottom:1px solid #ffe1e7;
    color:#3f0011;
    vertical-align:middle;
}
.saved-table tr:hover{
    background:#fffafa;
}
.saved-badge{
    display:inline-flex;
    align-items:center;
    min-height:28px;
    padding:4px 10px;
    border-radius:999px;
    background:#fff1f4;
    color:#8a0015;
    border:1px solid #ffd1dc;
    font-weight:900;
}
.saved-action{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-height:34px;
    padding:0 12px;
    border-radius:999px;
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
    text-decoration:none;
    font-weight:950;
}
'''

if ".saved-section" not in t:
    t = t.replace("</style>", css + "\n</style>")

saved_block = r'''
<section class="card saved-section">
    <div class="head">
        <h2>Hồ sơ đã lưu</h2>
        <p>Danh sách student đã có hồ sơ trong hệ thống.</p>
    </div>

    <div class="body">
        <div class="saved-table-wrap">
            <table class="saved-table">
                <thead>
                    <tr>
                        <th>ID student</th>
                        <th>Tên</th>
                        <th>Gmail</th>
                        <th>Số điện thoại</th>
                        <th>Account</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in saved_profiles %}
                        <tr>
                            <td>
                                <span class="saved-badge">
                                    {% if item.student_id %}
                                        {{ item.student_id }}
                                    {% else %}
                                        Chưa có
                                    {% endif %}
                                </span>
                            </td>

                            <td>
                                {% if item.full_name %}
                                    {{ item.full_name }}
                                {% elif item.name %}
                                    {{ item.name }}
                                {% elif item.user.first_name %}
                                    {{ item.user.first_name }}
                                {% else %}
                                    Chưa có
                                {% endif %}
                            </td>

                            <td>
                                {% if item.email %}
                                    {{ item.email }}
                                {% elif item.gmail %}
                                    {{ item.gmail }}
                                {% elif item.user.email %}
                                    {{ item.user.email }}
                                {% else %}
                                    Chưa có
                                {% endif %}
                            </td>

                            <td>
                                {% if item.phone %}
                                    {{ item.phone }}
                                {% elif item.phone_number %}
                                    {{ item.phone_number }}
                                {% elif item.sdt %}
                                    {{ item.sdt }}
                                {% else %}
                                    Chưa có
                                {% endif %}
                            </td>

                            <td>{{ item.user.username }}</td>

                            <td>
                                <a class="saved-action" href="?profile_id={{ item.id }}&q={{ item.user.email|urlencode }}">
                                    Mở hồ sơ
                                </a>
                            </td>
                        </tr>
                    {% empty %}
                        <tr>
                            <td colspan="6">Chưa có hồ sơ student nào.</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</section>
'''

if "Hồ sơ đã lưu" not in t:
    t = t.replace("</div>\n</body>", "</div>\n" + saved_block + "\n</body>")

tpl.write_text(t, encoding="utf-8")

print("DA_THEM_DANH_SACH_HO_SO_DA_LUU")
