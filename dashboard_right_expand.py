from pathlib import Path
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_dashboard_right_expand_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

css_dir = Path("static/css")
css_dir.mkdir(parents=True, exist_ok=True)

css_file = css_dir / "dashboard_right_expand.css"

if css_file.exists():
    shutil.copy2(css_file, backup_dir / "dashboard_right_expand.css")

css_file.write_text(r'''
/* Expand right dashboard content only */
body {
    overflow-x: hidden !important;
}

/* Sidebar is compact, so content starts closer to the left */
.main-content,
.dashboard-main,
.content,
main {
    margin-left: 260px !important;
    width: calc(100vw - 260px) !important;
    max-width: none !important;
    padding-left: 28px !important;
    padding-right: 28px !important;
}

/* Make dashboard content/card wider */
.dashboard-content,
.dashboard-shell,
.admin-content,
.page-content,
.content-shell,
.container,
.container-fluid {
    width: 100% !important;
    max-width: none !important;
}

/* Big white/pink panels */
.dashboard-card,
.hero-card,
.admin-hero,
.card,
.panel,
.section-card {
    max-width: none !important;
}

/* Make the right preview/interface area larger */
iframe,
.preview-frame,
.student-preview,
.interface-preview,
.dashboard-iframe {
    width: 100% !important;
    max-width: none !important;
    min-height: 720px !important;
}

/* If preview is inside a wrapper, expand wrapper too */
.preview-wrap,
.preview-wrapper,
.iframe-wrap,
.iframe-wrapper,
.student-interface-wrap {
    width: 100% !important;
    max-width: none !important;
}

/* Reduce empty gap caused by old sidebar size */
@media (min-width: 900px) {
    .main-content,
    .dashboard-main,
    .content,
    main {
        margin-left: 260px !important;
        width: calc(100vw - 260px) !important;
    }
}
''', encoding="utf-8")

# Load CSS into templates
for path in Path("templates").rglob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "dashboard_right_expand.css" in text:
        continue

    if "</head>" in text:
        if "{% load static %}" not in text:
            text = "{% load static %}\n" + text
        text = text.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/dashboard_right_expand.css\' %}">\n</head>'
        )
        path.write_text(text, encoding="utf-8")
        print("Loaded CSS in:", path)

print("DONE: right dashboard content expanded.")
print("Backup:", backup_dir)
