from pathlib import Path
import re

# ==================================================
# 1) Edit view: khi lưu Version A, tự cố định question_text = Person 1-4
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

# Thay đoạn lấy question_text từ form nếu có
s = re.sub(
    r'voice\.question_text\s*=\s*request\.POST\.get\(prefix \+ "question_text", ""\)\.strip\(\)\s*or\s*f"Person \{voice\.order\}"',
    'voice.question_text = f"Person {voice.order}"',
    s
)

s = re.sub(
    r'voice\.question_text\s*=\s*request\.POST\.get\(prefix \+ "question_text", ""\)\.strip\(\)',
    'voice.question_text = f"Person {voice.order}"',
    s
)

# Nếu có dạng không dùng prefix
s = re.sub(
    r'voice\.question_text\s*=\s*request\.POST\.get\("question_text", ""\)\.strip\(\)',
    'voice.question_text = f"Person {voice.order}"',
    s
)

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) Edit template admin Version A: bỏ ô nhập Question / Person, hiện text cố định
# ==================================================
admin_tpl = Path("templates/core/admin_part2_gioi_detail.html")
t = admin_tpl.read_text(encoding="utf-8", errors="ignore")

# Đổi tiêu đề cột
t = t.replace("Question / Person", "Person")

# Thay toàn bộ ô textarea questions/person thành text cố định
t = re.sub(
    r'''<td class="question-col">\s*
                            <textarea name="voice_\{\{ voice\.id \}\}_question_text"[\s\S]*?</textarea>\s*
                        </td>''',
    '''<td class="question-col">
                            <div class="fixed-person">Person {{ voice.order }}</div>
                        </td>''',
    t
)

# Nếu template đang có textarea dạng khác
t = re.sub(
    r'''<textarea name="voice_\{\{ voice\.id \}\}_question_text"[\s\S]*?</textarea>''',
    '''<div class="fixed-person">Person {{ voice.order }}</div>''',
    t
)

# Add CSS cho fixed-person
if ".fixed-person" not in t:
    t = t.replace(
        "</style>",
        """
.fixed-person{
    min-height:64px;
    display:flex;
    align-items:center;
    font-size:22px;
    font-weight:900;
    color:#111827;
    padding:12px 14px;
    border:1px solid #ffd1dc;
    border-radius:14px;
    background:#fffafa;
}
</style>"""
    )

admin_tpl.write_text(t, encoding="utf-8")


# ==================================================
# 3) Edit template student Version A: luôn hiện Person 1-4 cố định
# ==================================================
student_tpl = Path("templates/core/student_part2_gioi.html")
h = student_tpl.read_text(encoding="utf-8", errors="ignore")

# Thay phần hiển thị tên person
h = re.sub(
    r'''\{\{ voice\.question_text\|default:"Person" \}\}''',
    '''Person {{ voice.order }}''',
    h
)

h = re.sub(
    r'''\{\{ voice\.question_text\|default:"Question chưa nhập" \}\}''',
    '''Person {{ voice.order }}''',
    h
)

h = re.sub(
    r'''\{\{ voice\.question_text \}\}''',
    '''Person {{ voice.order }}''',
    h
)

student_tpl.write_text(h, encoding="utf-8")


# ==================================================
# 4) Chuẩn hóa data cũ trong database local: set lại Person 1-4
# ==================================================
Path("fix_part2_gioi_person_labels.py").write_text(r'''
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Part2Topic

for topic in Part2Topic.objects.filter(version="gioi"):
    for voice in topic.voices.all():
        if voice.order in [1, 2, 3, 4]:
            voice.question_text = f"Person {voice.order}"
            voice.save()

print("DA_CO_DINH_PERSON_1_4_CHO_MAY_GIOI")
''', encoding="utf-8")

print("DA_SUA_TEMPLATE_ADMIN_VA_HOC_VIEN_MAY_GIOI_PERSON_CO_DINH")
