from pathlib import Path
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_sidebar_size_only_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)

css_file = css_dir / "sidebar_size_only.css"

if css_file.exists():
    shutil.copy2(css_file, backup_dir / "sidebar_size_only.css")

css_file.write_text(r'''
/* Sidebar size only - no hiding, no deleting */
.sidebar,
.admin-sidebar,
.dashboard-sidebar,
.side-panel,
.left-sidebar,
aside {
    width: 260px !important;
    padding: 22px 18px !important;
    display: flex !important;
    flex-direction: column !important;
}

.sidebar .logo,
.admin-sidebar .logo,
.dashboard-sidebar .logo,
.side-panel .logo,
.left-sidebar .logo {
    transform: scale(0.86) !important;
    transform-origin: left top !important;
    margin-bottom: 20px !important;
}

.sidebar a,
.admin-sidebar a,
.dashboard-sidebar a,
.side-panel a,
.left-sidebar a,
.side-link,
.sidebar-link,
.menu-link,
.nav-link {
    min-height: 44px !important;
    padding: 11px 16px !important;
    margin: 7px 0 !important;
    border-radius: 16px !important;
    font-size: 17px !important;
    line-height: 1.18 !important;
    letter-spacing: -0.2px !important;
}

.sidebar a *,
.admin-sidebar a *,
.dashboard-sidebar a *,
.side-panel a *,
.left-sidebar a *,
.side-link *,
.sidebar-link *,
.menu-link *,
.nav-link * {
    font-size: inherit !important;
    line-height: inherit !important;
}

/* Make icons a bit smaller */
.sidebar a > :first-child,
.admin-sidebar a > :first-child,
.dashboard-sidebar a > :first-child,
.side-panel a > :first-child,
.left-sidebar a > :first-child {
    font-size: 18px !important;
}

/* Logout: smaller, lower, left */
a[href*="logout"],
a[href*="dang-xuat"],
.logout,
.logout-btn,
.logout-link {
    margin-top: auto !important;
    margin-left: 0 !important;
    margin-right: auto !important;
    margin-bottom: 26px !important;
    width: auto !important;
    max-width: 150px !important;
    min-height: 34px !important;
    padding: 9px 14px !important;
    border-radius: 13px !important;
    font-size: 14px !important;
    align-self: flex-start !important;
}

/* Adjust main content when sidebar is narrower */
.main-content,
.dashboard-main,
.content,
main {
    margin-left: 260px !important;
}
''', encoding="utf-8")

# Load CSS into HTML templates safely
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sidebar_size_only.css" in text:
        continue

    if "</head>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/sidebar_size_only.css\' %}">\n</head>'
        )
        path.write_text(text, encoding="utf-8")
        print("Loaded CSS in:", path)

print("DONE: sidebar made smaller only.")
print("Backup:", backup_dir)
