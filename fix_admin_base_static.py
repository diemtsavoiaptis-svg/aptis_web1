from pathlib import Path
import re

p = Path("templates/admin/base_site.html")
s = p.read_text(encoding="utf-8-sig", errors="ignore")

# Delete link font_theme.css bị đặt sai trên đầu file
s = re.sub(
    r'\s*<link rel="stylesheet" href="\{% static \'core/css/font_theme\.css\' %\}">\s*',
    '\n',
    s
)

# Delete các load static/i18n static lặp linh tinh ở đầu để dựng lại chuẩn
s = re.sub(r'^\s*\{% load static %\}\s*', '', s)
s = re.sub(r'^\s*\{% load i18n static %\}\s*', '', s)

# Đảm bảo extends đứng sau load
s = re.sub(r'^\s*\ufeff?', '', s)

if '{% extends "admin/base.html" %}' in s:
    s = s.replace('{% extends "admin/base.html" %}', '', 1)

s = '{% load i18n static %}\n{% extends "admin/base.html" %}\n' + s.lstrip()

# Chèn CSS font_theme vào block extrastyle nếu chưa có
font_link = '<link rel="stylesheet" href="{% static \'core/css/font_theme.css\' %}">'

if "core/css/font_theme.css" not in s:
    if "{% block extrastyle %}" in s:
        s = s.replace(
            "{% block extrastyle %}",
            "{% block extrastyle %}\n{{ block.super }}\n" + font_link,
            1
        )
    else:
        s += f"""

{{% block extrastyle %}}
{{{{ block.super }}}}
{font_link}
{{% endblock %}}
"""

# Nếu bị lặp {{ block.super }} ngay sau sửa thì gọn lại
s = s.replace("{{ block.super }}\n{{ block.super }}", "{{ block.super }}")

p.write_text(s, encoding="utf-8")
print("DA_SUA_ADMIN_BASE_SITE_STATIC_LOAD")
