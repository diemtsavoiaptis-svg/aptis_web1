from pathlib import Path
import re
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_sidebar_cleanup_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

targets = []
for root in ["templates", "static"]:
    p = Path(root)
    if p.exists():
        targets += [x for x in p.rglob("*") if x.suffix.lower() in [".html", ".css", ".js"]]

removed_files = []

for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "Tổng quan Admin" in text:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))

        # Remove common one-line menu links/buttons containing Tổng quan Admin
        text = re.sub(
            r'(?im)^\s*<a\b[^>]*>[^<]*(?:<[^>]+>[^<]*)*Tổng quan Admin[^<]*(?:<[^>]+>[^<]*)*</a>\s*\n?',
            "",
            text,
        )
        text = re.sub(
            r'(?im)^\s*<button\b[^>]*>[^<]*(?:<[^>]+>[^<]*)*Tổng quan Admin[^<]*(?:<[^>]+>[^<]*)*</button>\s*\n?',
            "",
            text,
        )
        text = re.sub(
            r'(?is)\s*<li\b[^>]*>\s*<a\b[^>]*>.*?Tổng quan Admin.*?</a>\s*</li>',
            "",
            text,
        )

        # Remove simple div/card blocks if the whole block is only that menu item
        text = re.sub(
            r'(?is)\s*<div\b([^>]*)>\s*<a\b[^>]*>.*?Tổng quan Admin.*?</a>\s*</div>',
            "",
            text,
        )

        if text != original:
            path.write_text(text, encoding="utf-8")
            removed_files.append(str(path))

# Add/override sidebar compact CSS
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
css_file = css_dir / "sidebar_compact_fix.css"

css_file.write_text(r'''
/* Sidebar compact fix - remove overview spacing and make menu smaller */
.sidebar,
.admin-sidebar,
.dashboard-sidebar,
.side-panel,
.left-sidebar,
aside {
    display: flex;
    flex-direction: column;
}

.sidebar a,
.admin-sidebar a,
.dashboard-sidebar a,
.side-panel a,
.left-sidebar a,
.side-link,
.sidebar-link,
.nav-link,
.menu-link {
    min-height: 44px !important;
    padding: 12px 18px !important;
    margin: 8px 0 !important;
    border-radius: 16px !important;
    font-size: 18px !important;
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
.nav-link *,
.menu-link * {
    font-size: inherit !important;
    line-height: inherit !important;
}

.sidebar .active,
.admin-sidebar .active,
.dashboard-sidebar .active,
.side-panel .active,
.left-sidebar .active {
    transform: none !important;
}

/* Logout smaller and lower-left */
a[href*="logout"],
a[href*="dang-xuat"],
.logout,
.logout-btn,
.logout-link {
    margin-top: auto !important;
    margin-left: 0 !important;
    margin-right: auto !important;
    margin-bottom: 28px !important;
    width: auto !important;
    max-width: 220px !important;
    min-height: 38px !important;
    padding: 10px 16px !important;
    font-size: 15px !important;
    border-radius: 14px !important;
    align-self: flex-start !important;
}
''', encoding="utf-8")

# Ensure CSS is loaded in base/templates if possible
for path in [p for p in targets if p.suffix.lower() == ".html"]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sidebar_compact_fix.css" in text:
        continue
    if "</head>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/sidebar_compact_fix.css\' %}">\n</head>'
        )
        path.write_text(text, encoding="utf-8")

print("Removed/updated files:")
for f in removed_files:
    print("-", f)
print("CSS added:", css_file)
print("Backup:", backup_dir)
