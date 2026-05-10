from pathlib import Path
import re

p = Path("core/admin.py")
s = p.read_text(encoding="utf-8", errors="ignore")

backup = Path("core/admin.py.bak_fix_part2_duplicate_admin")
backup.write_text(s, encoding="utf-8")

# Xóa toàn bộ các block Admin Part 2 cũ bị lặp
s = re.sub(
    r"\n?# ===== Admin Part 2 =====[\s\S]*?# ===== End Admin Part 2 =====\n?",
    "\n",
    s
)

# Xóa các class Part2 admin cũ nếu còn sót
s = re.sub(
    r"\n?class\s+Part2VoiceInline\(admin\.TabularInline\):[\s\S]*?(?=\nclass |\n@admin\.register|\n#|\Z)",
    "\n",
    s
)

s = re.sub(
    r"\n?@admin\.register\(Part2Topic\)\s*\nclass\s+Part2TopicAdmin\(admin\.ModelAdmin\):[\s\S]*?(?=\n@admin\.register|\nclass |\n#|\Z)",
    "\n",
    s
)

s = re.sub(
    r"\n?@admin\.register\(Part2Voice\)\s*\nclass\s+Part2VoiceAdmin\(admin\.ModelAdmin\):[\s\S]*?(?=\n@admin\.register|\nclass |\n#|\Z)",
    "\n",
    s
)

# Đảm bảo import Part2Topic, Part2Voice có trong dòng import model
if "Part2Topic" not in s or "Part2Voice" not in s:
    if "from .models import" in s:
        s = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic, Part2Voice",
            s,
            count=1
        )
    else:
        s = "from .models import Part2Topic, Part2Voice\n" + s

# Thêm lại duy nhất 1 block Admin Part 2, có unregister an toàn trước khi register
part2_admin_block = r'''

# ===== Admin Part 2 =====
from django.contrib.admin.sites import NotRegistered

try:
    admin.site.unregister(Part2Topic)
except NotRegistered:
    pass

try:
    admin.site.unregister(Part2Voice)
except NotRegistered:
    pass


class Part2VoiceInline(admin.TabularInline):
    model = Part2Voice
    extra = 4
    fields = (
        "order",
        "audio_url",
        "answer_a",
        "answer_b",
        "answer_c",
        "answer_d",
        "transcript",
        "data_choices",
        "correct_answer",
    )


@admin.register(Part2Topic)
class Part2TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "description")
    inlines = [Part2VoiceInline]


@admin.register(Part2Voice)
class Part2VoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "order", "correct_answer")
    list_filter = ("topic", "correct_answer")
    search_fields = ("topic__title", "transcript", "data_choices")
# ===== End Admin Part 2 =====
'''

s = s.rstrip() + "\n" + part2_admin_block + "\n"

# Dọn dòng trắng quá nhiều
s = re.sub(r"\n{4,}", "\n\n\n", s)

p.write_text(s, encoding="utf-8")
print("DA_SUA_LOI_PART2_ADMIN_BI_DANG_KY_LAP")
