from pathlib import Path

p = Path("static/core/css/font_theme.css")
s = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

extra = r'''

/* Giảm kích thước tiêu đề toàn web */
h1 {
    font-size: clamp(26px, 3vw, 38px) !important;
    line-height: 1.18 !important;
}

h2 {
    font-size: clamp(22px, 2.2vw, 30px) !important;
    line-height: 1.22 !important;
}

h3 {
    font-size: clamp(18px, 1.7vw, 24px) !important;
    line-height: 1.28 !important;
}

.topbar h1,
.admin-header h1,
.aptis-part-name {
    font-size: clamp(26px, 3vw, 38px) !important;
}
'''

if "Giảm kích thước tiêu đề toàn web" not in s:
    s += extra

p.write_text(s, encoding="utf-8")
print("DA_GIAM_CHU_TIEU_DE_TOAN_WEB")
