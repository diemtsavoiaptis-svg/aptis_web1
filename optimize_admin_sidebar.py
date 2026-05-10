from pathlib import Path

p = Path("templates/admin/base_site.html")
s = p.read_text(encoding="utf-8", errors="ignore")

extra_css = r'''
/* Tối ưu sidebar Django Admin: ẩn cột "+ Thêm vào", gọn dễ thao tác */
#nav-sidebar .addlink,
#nav-sidebar td.addlink,
#nav-sidebar th.addlink,
#nav-sidebar a.addlink,
#nav-sidebar .model-addlink,
#nav-sidebar .add-row,
#nav-sidebar td:last-child a.addlink {
    display: none !important;
}

/* Làm sidebar chỉ còn danh sách mục quản lý */
#nav-sidebar table {
    width: 100% !important;
}

#nav-sidebar table th,
#nav-sidebar table td {
    padding: 0 !important;
}

#nav-sidebar table td:last-child {
    display: none !important;
}

#nav-sidebar .module th,
#nav-sidebar .module td {
    border-bottom: 1px solid rgba(230, 0, 35, 0.10) !important;
}

/* Tối ưu ô tìm kiếm */
#nav-filter {
    width: calc(100% - 20px) !important;
    margin: 10px !important;
    padding: 12px 14px !important;
    border-radius: 14px !important;
    border: 1px solid #ffd1dc !important;
    background: #fffafa !important;
    color: #3f0011 !important;
    font-size: 16px !important;
}

/* Nhóm tiêu đề bên trái */
#nav-sidebar caption,
#nav-sidebar .module caption {
    padding: 14px 18px !important;
    background: linear-gradient(135deg, #e60023, #ff5f76) !important;
    color: white !important;
    font-weight: 900 !important;
    letter-spacing: .03em !important;
    text-align: left !important;
}

/* Link model dễ đọc, gọn hơn */
#nav-sidebar .module th a,
#nav-sidebar .module td a {
    display: block !important;
    padding: 13px 18px !important;
    color: #7a0010 !important;
    font-weight: 850 !important;
    font-size: 17px !important;
    line-height: 1.25 !important;
    text-decoration: none !important;
}

/* Hover và dòng đang chọn */
#nav-sidebar .module th a:hover,
#nav-sidebar .module td a:hover {
    background: #fff1f4 !important;
    color: #e60023 !important;
}

#nav-sidebar .current-model {
    background: #fff8b8 !important;
}

#nav-sidebar .current-model a {
    color: #5b0010 !important;
    font-weight: 950 !important;
}

/* Giảm độ rộng sidebar để phần nội dung rộng hơn */
#nav-sidebar {
    width: 270px !important;
    background: #fff7f9 !important;
    border-right: 1px solid #ffd1dc !important;
}

.main.shifted > #nav-sidebar + .content,
#content {
    max-width: none !important;
}

/* Làm chữ tiếng Việt không bị lỗi khoảng cách */
#nav-sidebar,
#nav-sidebar * {
    word-break: normal !important;
    overflow-wrap: anywhere !important;
}
'''

marker = "Tối ưu sidebar Django Admin: ẩn cột"
if marker not in s:
    if "{% block extrastyle %}" in s:
        s = s.replace("{% endblock %}", extra_css + "\n{% endblock %}", 1)
    else:
        s += f"""

{{% block extrastyle %}}
{{{{ block.super }}}}
<style>
{extra_css}
</style>
{{% endblock %}}
"""
else:
    print("CSS_DA_CO_SAN")

# Nếu extra_css chưa nằm trong thẻ style thì bọc lại
if marker in s and "<style>" not in s[s.find(marker)-50:s.find(marker)+50]:
    s = s.replace(extra_css, "<style>\n" + extra_css + "\n</style>")

p.write_text(s, encoding="utf-8")
print("DA_AN_COT_THEM_VAO_VA_TOI_UU_ADMIN_SIDEBAR")
