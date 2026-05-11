from pathlib import Path
import unicodedata
import re

# 1) Chuẩn hóa toàn bộ file text sang UTF-8 NFC để dấu tiếng Việt không bị tách
exts = {".py", ".html", ".css", ".js", ".txt", ".md"}
folders = ["core", "templates", "static", "config"]

changed = []

for folder in folders:
    root = Path(folder)
    if not root.exists():
        continue

    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                s = p.read_text(encoding="utf-8-sig", errors="ignore")
                ns = unicodedata.normalize("NFC", s)

                # Edit một số chữ hay bị tách dấu do copy/paste
                fixes = {
                    "Hồ sơ": "Hồ sơ",
                    "hồ sơ": "hồ sơ",
                    "cần": "cần",
                    "Cần": "Cần",
                    "cần tra": "cần tra",
                    "đã lưu": "đã lưu",
                    "Đã lưu": "Đã lưu",
                    "quản lý": "manage",
                    "Quản lý": "Manage",
                    "chọn": "chọn",
                    "Chọn": "Chọn",
                    "học viên": "student",
                    "Học viên": "Student",
                    "đăng nhập": "đăng nhập",
                    "Đăng nhập": "Login",
                    "mật khẩu": "mật khẩu",
                    "Mật khẩu": "Password",
                }

                for a, b in fixes.items():
                    ns = ns.replace(a, b)

                if ns != s:
                    p.write_text(ns, encoding="utf-8")
                    changed.append(str(p))
            except Exception as e:
                print("SKIP", p, e)

# 2) Tạo CSS font tiếng Việt chuẩn, tránh Georgia làm vỡ dấu
font_css = Path("static/core/css/font_theme.css")
font_css.parent.mkdir(parents=True, exist_ok=True)

font_css.write_text("""
/* Font tiếng Việt chuẩn cho toàn bộ web */
:root {
    --font-vietnamese: "Segoe UI", Tahoma, Arial, "Helvetica Neue", sans-serif;
}

html, body,
button, input, textarea, select,
.card, .head, .body,
.side-link, .brand-title, .brand-sub,
.saved-table, .student-admin-wrap,
.admin-shell, .admin-sidebar, .admin-main {
    font-family: var(--font-vietnamese) !important;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
}

/* Title vẫn đậm, mượt nhưng không vỡ dấu */
h1, h2, h3, h4,
.profile-title,
#panelTitle,
.frame-label,
.card-head h2,
.head h2 {
    font-family: var(--font-vietnamese) !important;
    font-weight: 900 !important;
    letter-spacing: -0.025em;
}
""", encoding="utf-8")

# 3) Đảm bảo các template chính đều load font_theme.css
for p in Path("templates").rglob("*.html"):
    s = p.read_text(encoding="utf-8-sig", errors="ignore")
    ns = unicodedata.normalize("NFC", s)

    if "font_theme.css" not in ns and "</head>" in ns:
        if "{% load static %}" not in ns[:300]:
            ns = "{% load static %}\n" + ns

        ns = ns.replace(
            "</head>",
            '<link rel="stylesheet" href="{% static \'core/css/font_theme.css\' %}">\n</head>',
            1
        )

    if ns != s:
        p.write_text(ns, encoding="utf-8")
        changed.append(str(p))

print("DA_CHUAN_HOA_TIENg_VIET_UTF8_NFC")
print("SO_FILE_DA_SUA:", len(set(changed)))
for x in sorted(set(changed))[:80]:
    print("-", x)
