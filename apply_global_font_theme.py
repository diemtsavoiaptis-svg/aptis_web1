from pathlib import Path
import re

css_dir = Path("static/core/css")
css_dir.mkdir(parents=True, exist_ok=True)

Path("static/core/css/font_theme.css").write_text(r'''
:root {
    --font-main: Georgia, "Times New Roman", "Times New Roman Vietnamese", serif;
    --font-ui: Georgia, "Times New Roman", serif;
}

html, body,
button, input, textarea, select,
a, p, span, div, label, table, th, td,
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-main) !important;
}

body {
    font-size: 17px;
    line-height: 1.65;
    letter-spacing: -0.01em;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 900 !important;
    letter-spacing: -0.035em;
    line-height: 1.15;
}

h1 {
    font-size: clamp(36px, 4.5vw, 58px);
}

h2 {
    font-size: clamp(28px, 3vw, 40px);
}

h3 {
    font-size: clamp(22px, 2vw, 30px);
}

button,
.btn,
.primary-btn,
.ghost-btn,
.side-link,
.aptis-part-btn {
    font-weight: 900 !important;
    letter-spacing: -0.015em;
}

input,
textarea,
select {
    font-size: 16px !important;
}

.muted,
.aptis-parts-subtitle,
.admin-header p,
.topbar p {
    font-size: 17px;
    line-height: 1.7;
}

.brand strong,
.brand-name,
.aptis-part-name {
    font-family: var(--font-main) !important;
    font-weight: 900 !important;
}

.lesson-item,
.part-card,
.aptis-part-card,
.stat-card,
.question-card,
.bulk-card,
.toolbar-card {
    font-family: var(--font-main) !important;
}
''', encoding="utf-8")

templates = list(Path("templates").rglob("*.html"))

for p in templates:
    text = p.read_text(encoding="utf-8", errors="ignore")

    if "core/css/font_theme.css" in text:
        continue

    link = '<link rel="stylesheet" href="{% static \'core/css/font_theme.css\' %}">'

    if "{% load static %}" not in text:
        text = "{% load static %}\n" + text

    if "</head>" in text:
        text = text.replace("</head>", f"    {link}\n</head>", 1)
    else:
        text = link + "\n" + text

    p.write_text(text, encoding="utf-8")

print("DA_DOI_FONT_TOAN_BO_WEB_THANH_SERIF_DO_DEP")
