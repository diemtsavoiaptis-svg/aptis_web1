from pathlib import Path
import shutil
import re

print("=== RESTORE SIDEBAR FILES THEN REMOVE ONLY OVERVIEW ===")

# 1) Restore from latest sidebar cleanup backup
backup_dirs = sorted(Path("code_backups").glob("before_sidebar_cleanup_*"))
if backup_dirs:
    latest = backup_dirs[-1]
    print("Restoring from:", latest)

    for backup_file in latest.iterdir():
        if not backup_file.is_file():
            continue

        # backup name example: templates__core__dashboard.html
        original_path = Path(str(backup_file.name).replace("__", "/"))
        original_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_file, original_path)
        print("Restored:", original_path)
else:
    print("No sidebar backup found. Continuing with current files.")

# 2) Remove ONLY the exact sidebar item "Tổng quan Admin"
targets = []
for root in ["templates"]:
    p = Path(root)
    if p.exists():
        targets += [x for x in p.rglob("*.html")]

for path in targets:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Remove only one <a> element containing exact text Tổng quan Admin
    text = re.sub(
        r'(?is)\s*<a\b(?=[^>]*(?:class|href))[^>]*>.*?Tổng quan Admin.*?</a>\s*',
        "\n",
        text,
        count=1
    )

    # Remove empty li wrapper if left behind
    text = re.sub(r'(?is)<li[^>]*>\s*</li>', '', text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("Removed only Tổng quan Admin from:", path)

# 3) Compact sidebar CSS only, no deleting more menu items
css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)
css_file = css_dir / "sidebar_compact_fix.css"

css_file.write_text(r'''
/* Compact sidebar only - do not hide menu items */
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
    min-height: 42px !important;
    padding: 11px 16px !important;
    margin: 7px 0 !important;
    border-radius: 15px !important;
    font-size: 17px !important;
    line-height: 1.18 !important;
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

/* Logout lower-left and smaller */
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
    max-width: 210px !important;
    min-height: 36px !important;
    padding: 9px 15px !important;
    font-size: 14px !important;
    border-radius: 13px !important;
    align-self: flex-start !important;
}
''', encoding="utf-8")

# 4) Ensure CSS loaded
for path in targets:
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

print("DONE")
