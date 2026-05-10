from pathlib import Path
import re

p = Path("templates/core/dashboard.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Backup
Path("templates/core/dashboard.html.bak_fix_admin_links").write_text(s, encoding="utf-8")

# Ép các menu admin thành link thật, không dùng iframe/button nữa
replacements = [
    (
        r'<button class="side-link"[^>]*>\s*✅\s*Duyệt học viên\s*</button>',
        '<a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt học viên</a>'
    ),
    (
        r'<button class="side-link"[^>]*>\s*📚\s*Quản lý bài học\s*</button>',
        '<a class="side-link" href="/admin/core/lesson/">📚 Quản lý bài học</a>'
    ),
    (
        r'<button class="side-link"[^>]*>\s*🛡️\s*Cảnh báo bảo mật\s*</button>',
        '<a class="side-link" href="/admin/core/securityalert/">🛡️ Cảnh báo bảo mật</a>'
    ),
]

for pattern, repl in replacements:
    s = re.sub(pattern, repl, s, flags=re.S)

# Nếu nó đã là thẻ a nhưng href sai thì sửa lại
s = re.sub(
    r'<a class="side-link"[^>]*>\s*✅\s*Duyệt học viên\s*</a>',
    '<a class="side-link" href="/admin/core/studentprofile/">✅ Duyệt học viên</a>',
    s,
    flags=re.S
)

s = re.sub(
    r'<a class="side-link"[^>]*>\s*📚\s*Quản lý bài học\s*</a>',
    '<a class="side-link" href="/admin/core/lesson/">📚 Quản lý bài học</a>',
    s,
    flags=re.S
)

s = re.sub(
    r'<a class="side-link"[^>]*>\s*🛡️\s*Cảnh báo bảo mật\s*</a>',
    '<a class="side-link" href="/admin/core/securityalert/">🛡️ Cảnh báo bảo mật</a>',
    s,
    flags=re.S
)

p.write_text(s, encoding="utf-8")
print("DA_SUA_LINK_DUYET_HOC_VIEN_ADMIN")
