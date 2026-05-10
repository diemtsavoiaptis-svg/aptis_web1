from pathlib import Path

p = Path("static/core/css/font_theme.css")
s = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

extra = r'''

/* Ẩn danh sách câu hỏi bên giao diện học viên */
.question-side,
.side-card,
.question-numbers,
.side-stats {
    display: none !important;
}

.student-layout {
    grid-template-columns: 1fr !important;
    max-width: 980px !important;
}

.exam-panel {
    width: 100% !important;
}
'''

if "Ẩn danh sách câu hỏi bên giao diện học viên" not in s:
    s += extra

p.write_text(s, encoding="utf-8")
print("DA_AN_DANH_SACH_CAU_HOI_HOC_VIEN")
