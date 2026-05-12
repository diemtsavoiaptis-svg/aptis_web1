from pathlib import Path
import re
import shutil
from datetime import datetime

print("=== FIX LAYOUT SAFELY: KEEP SIDEBAR, EXPAND RIGHT CONTENT ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_safe_layout_fix_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# 1) Xoá CSS phóng to sai vừa thêm
bad_css = Path("static/css/dashboard_right_expand.css")
if bad_css.exists():
    shutil.copy2(bad_css, backup_dir / "dashboard_right_expand.css")
    bad_css.unlink()
    print("Deleted wrong CSS:", bad_css)

# 2) Gỡ dòng nạp dashboard_right_expand.css khỏi template
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    text = re.sub(r'\s*<link[^>]+dashboard_right_expand\.css[^>]*>\s*', "\n", text)

    if text != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(text, encoding="utf-8")
        print("Removed wrong CSS link from:", path)

# 3) Thêm CSS layout an toàn: sidebar cố định, phần phải rộng nhưng không bị ẩn
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
safe_css = css_dir / "safe_dashboard_layout.css"

safe_css.write_text(r'''
/* Safe dashboard layout: keep sidebar, expand right content */
body {
    overflow-x: hidden !important;
}

/* Keep left sidebar visible */
.sidebar,
.admin-sidebar,
.dashboard-sidebar,
.side-panel,
.left-sidebar,
aside {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    z-index: 20 !important;
}

/* Right content starts after sidebar */
main,
.main-content,
.dashboard-main,
.content,
.page-content,
.admin-main {
    margin-left: 260px !important;
    width: calc(100vw - 260px) !important;
    max-width: calc(100vw - 260px) !important;
    min-height: 100vh !important;
    padding-left: 28px !important;
    padding-right: 28px !important;
    box-sizing: border-box !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Expand inner cards without hiding them */
.dashboard-content,
.dashboard-shell,
.admin-content,
.content-shell,
.container,
.container-fluid,
.hero-card,
.admin-hero,
.dashboard-card,
.card,
.panel,
.section-card {
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* Preview/frame grows inside available space */
iframe,
.preview-frame,
.student-preview,
.interface-preview,
.dashboard-iframe {
    width: 100% !important;
    max-width: 100% !important;
}
''', encoding="utf-8")

# 4) Nạp CSS an toàn vào templates
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "safe_dashboard_layout.css" in text:
        continue

    if "</head>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/safe_dashboard_layout.css\' %}">\n</head>'
        )
        path.write_text(text, encoding="utf-8")
        print("Loaded safe CSS in:", path)

print("DONE")
print("Backup:", backup_dir)
