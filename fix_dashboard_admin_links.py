from pathlib import Path
import re

p = Path("templates/core/dashboard.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Backup
Path("templates/core/dashboard.html.bak_fix_admin_links").write_text(s, encoding="utf-8")

# Ép các menu admin thành link thật, không dùng iframe/button nữa
replacements = [
    (
        r'<button class="side-link"[^>]*>\s*✅\s*Duyệt student\s*</button>',
        '<a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt student</a>'
    ),
    (
        r'<button class="side-link"[^>]*>\s*📚\s*Manage lesson\s*</button>',
        '<a class="side-link" href="/admin/core/lesson/">📚 Manage lesson</a>'
    ),
    (
        r'<button class="side-link"[^>]*>\s*🛡️\s*Security Alerts\s*</button>',
        '<a class="side-link" href="/admin/core/securityalert/">🛡️ Security Alerts</a>'
    ),
]

for pattern, repl in replacements:
    s = re.sub(pattern, repl, s, flags=re.S)

# Nếu nó đã là thẻ a nhưng href sai thì sửa lại
s = re.sub(
    r'<a class="side-link"[^>]*>\s*✅\s*Duyệt student\s*</a>',
    '<a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt student</a>',
    s,
    flags=re.S
)

s = re.sub(
    r'<a class="side-link"[^>]*>\s*📚\s*Manage lesson\s*</a>',
    '<a class="side-link" href="/admin/core/lesson/">📚 Manage lesson</a>',
    s,
    flags=re.S
)

s = re.sub(
    r'<a class="side-link"[^>]*>\s*🛡️\s*Security Alerts\s*</a>',
    '<a class="side-link" href="/admin/core/securityalert/">🛡️ Security Alerts</a>',
    s,
    flags=re.S
)

p.write_text(s, encoding="utf-8")
print("DA_SUA_LINK_DUYET_HOC_VIEN_ADMIN")
