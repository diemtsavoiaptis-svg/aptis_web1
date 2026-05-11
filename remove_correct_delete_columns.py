from pathlib import Path
import re

# 1) Edit template: xóa cột Đúng và cột Delete trong bảng Part 1
p = Path("templates/core/admin_part1_questions.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Delete CSS width của 2 cột
s = s.replace(".col-correct{width:90px}", "")
s = s.replace(".col-delete{width:90px}", "")

# Delete tiêu đề cột Đúng và Delete
s = re.sub(r'\s*<th class="col-correct">Đúng</th>', "", s)
s = re.sub(r'\s*<th class="col-delete">Delete</th>', "", s)

# Delete ô select answer đúng
s = re.sub(
    r'\s*<td>\s*<select name="correct_answer_\{\{ q\.id \}\}">.*?</select>\s*</td>',
    "",
    s,
    flags=re.S
)

# Delete ô nút Delete từng dòng
s = re.sub(
    r'\s*<td>\s*<button class="delete-btn".*?</button>\s*</td>',
    "",
    s,
    flags=re.S
)

# Edit colspan dòng rỗng từ 12 xuống 10
s = s.replace('colspan="12"', 'colspan="10"')

p.write_text(s, encoding="utf-8")
print("DA_XOA_COT_DUNG_VA_XOA")


# 2) Edit views.py: nếu không còn cột Đúng thì không tự ghi đè answer đúng thành A
vp = Path("core/views.py")
v = vp.read_text(encoding="utf-8", errors="ignore")

v = v.replace(
    'q.correct_answer = request.POST.get(f"correct_answer_{row_id}", "A").strip().upper()[:1] or "A"',
    'posted_correct = request.POST.get(f"correct_answer_{row_id}")\n                if posted_correct is not None:\n                    q.correct_answer = posted_correct.strip().upper()[:1] or q.correct_answer or "A"'
)

vp.write_text(v, encoding="utf-8")
print("DA_SUA_SAVE_ALL_KHONG_GHI_DE_DAP_AN")


# 3) Check và chạy lại server
