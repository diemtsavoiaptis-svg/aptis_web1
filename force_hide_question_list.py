from pathlib import Path
import re

p = Path("templates/core/listening.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Backup trước khi sửa
Path("templates/core/listening.html.bak_hide_question_list").write_text(s, encoding="utf-8")

# 1) Delete các block aside/section/div có chứa tiêu đề "Danh sách questions"
patterns = [
    r'<aside[^>]*>[\s\S]*?Danh sách questions[\s\S]*?</aside>',
    r'<section[^>]*>[\s\S]*?Danh sách questions[\s\S]*?</section>',
    r'<div[^>]*class="[^"]*(?:question-side|side-card|question-list|question-panel)[^"]*"[^>]*>[\s\S]*?Danh sách questions[\s\S]*?</div>\s*</div>',
]

old = s
for pat in patterns:
    s = re.sub(pat, "", s, flags=re.I, count=1)

# 2) Chèn CSS ép ẩn vào ngay template, phòng trường hợp còn sót class
force_css = r'''
<style id="force-hide-question-list">
    .question-side,
    .side-card,
    .question-numbers,
    .side-stats,
    .question-list,
    .question-panel,
    .student-sidebar,
    aside:has(.question-numbers),
    aside:has(.side-stats) {
        display: none !important;
        width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
    }

    .student-layout,
    .exam-layout,
    .listening-layout {
        grid-template-columns: 1fr !important;
        max-width: 980px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    .exam-panel,
    .listening-main,
    main {
        width: 100% !important;
    }
</style>
'''

if "force-hide-question-list" not in s:
    if "</head>" in s:
        s = s.replace("</head>", force_css + "\n</head>", 1)
    else:
        s = force_css + "\n" + s

p.write_text(s, encoding="utf-8")

print("DA_AN_DANH_SACH_CAU_HOI_TRONG_TEMPLATE")
print("DA_XOA_BLOCK:", s != old)
