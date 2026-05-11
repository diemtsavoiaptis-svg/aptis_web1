from pathlib import Path
import re

# 1) Ép Django cho phép iframe cùng domain
settings = Path("config/settings.py")
s = settings.read_text(encoding="utf-8", errors="ignore")

# Delete mọi dòng X_FRAME_OPTIONS cũ rồi thêm lại cuối file để thắng tất cả
s = re.sub(r"(?m)^X_FRAME_OPTIONS\s*=.*\n?", "", s)
s += '''

# Cho phép dashboard nhúng các trang nội bộ vào khung bên phải
X_FRAME_OPTIONS = "SAMEORIGIN"
'''
settings.write_text(s, encoding="utf-8")


# 2) Edit middleware bảo mật nếu nó đang tự set DENY
mw = Path("core/middleware.py")
if mw.exists():
    m = mw.read_text(encoding="utf-8", errors="ignore")

    # Nếu middleware set DENY thì đổi thành SAMEORIGIN
    m = m.replace('"DENY"', '"SAMEORIGIN"')
    m = m.replace("'DENY'", "'SAMEORIGIN'")

    # Nếu có setdefault X-Frame-Options thì cũng cho SAMEORIGIN
    m = re.sub(
        r'response\["X-Frame-Options"\]\s*=\s*["\'].*?["\']',
        'response["X-Frame-Options"] = "SAMEORIGIN"',
        m
    )

    mw.write_text(m, encoding="utf-8")


# 3) Đảm bảo nút Duyệt student mở đúng trang mới
dash = Path("templates/core/dashboard.html")
d = dash.read_text(encoding="utf-8", errors="ignore")

d = d.replace('data-url="/admin/core/studentprofile/"', 'data-url="/dashboard/students/"')

dash.write_text(d, encoding="utf-8")

print("DA_SUA_IFRAME_DUYET_HOC_VIEN_SAMEORIGIN")
