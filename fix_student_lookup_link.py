from pathlib import Path
import re

p = Path("templates/core/dashboard.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Đổi separate nút Duyệt student từ Django Admin cũ sang trang tra cứu mới
s = s.replace('data-url="/admin/core/studentprofile/"', 'data-url="/dashboard/students/"')

# Đổi quick-card student nếu có
s = s.replace('data-url="/admin/core/studentprofile/" data-title="Duyệt student"', 'data-url="/dashboard/students/" data-title="Duyệt student"')

p.write_text(s, encoding="utf-8")
print("DA_DOI_NUT_DUYET_HOC_VIEN_SANG_TRANG_TRA_CUU_MOI")
