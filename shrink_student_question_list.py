from pathlib import Path

p = Path("static/core/css/font_theme.css")
s = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

extra = r'''

/* Thu nhỏ khối danh sách câu hỏi bên học viên */
.question-side,
.side-card {
    max-width: 320px !important;
}

.side-card {
    padding: 14px !important;
    border-radius: 20px !important;
}

.side-card h3,
.side-card h2 {
    font-size: 22px !important;
    margin-bottom: 12px !important;
}

.side-stats {
    gap: 8px !important;
    margin: 10px 0 14px !important;
}

.side-stats div {
    padding: 10px !important;
    border-radius: 14px !important;
}

.side-stats strong {
    font-size: 28px !important;
}

.side-stats span {
    font-size: 13px !important;
}

.question-numbers {
    grid-template-columns: repeat(5, 1fr) !important;
    gap: 7px !important;
}

.question-numbers a {
    height: 38px !important;
    min-width: 38px !important;
    border-radius: 12px !important;
    font-size: 18px !important;
    font-weight: 900 !important;
}

.student-layout {
    grid-template-columns: minmax(0, 1fr) 320px !important;
    gap: 18px !important;
}

@media (max-width: 900px) {
    .student-layout {
        grid-template-columns: 1fr !important;
    }

    .question-side,
    .side-card {
        max-width: 100% !important;
    }

    .question-numbers {
        grid-template-columns: repeat(8, 1fr) !important;
    }

    .question-numbers a {
        height: 34px !important;
        min-width: 34px !important;
        font-size: 15px !important;
    }
}
'''

if "Thu nhỏ khối danh sách câu hỏi bên học viên" not in s:
    s += extra

p.write_text(s, encoding="utf-8")
print("DA_THU_NHO_DANH_SACH_CAU_HOI_HOC_VIEN")
