from pathlib import Path
import re

tpl = Path("templates/core/admin_part2_gioi_detail.html")
s = tpl.read_text(encoding="utf-8", errors="ignore")

# Backup trước khi sửa
Path("templates/core/admin_part2_gioi_detail.backup_before_save_total_button.html").write_text(s, encoding="utf-8")

# 1) Đảm bảo form đầu tiên là form lưu answer tổng
s = re.sub(
    r'(<form method="post">\s*\{% csrf_token %\}\s*)<input type="hidden" name="action" value="[^"]+">',
    r'\1<input type="hidden" name="action" value="save_total_answers">',
    s,
    count=1,
    flags=re.S
)

# 2) Nếu chưa có nút Save answer tổng thì chèn ngay trước section chọn answer đúng
if "Save answer tổng" not in s:
    button_block = '''
    <div class="actions save-total-actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Save answer tổng</button>
    </div>
'''

    # Chèn trước card chọn answer đúng
    patterns = [
        r'(\s*</section>\s*)(\s*<section class="card">\s*<h2[^>]*>\s*Choose answer đúng cho 4 person\s*</h2>)',
        r'(\s*</section>\s*)(\s*<section class="card">\s*<h2[^>]*>[\s\S]*?4 person[\s\S]*?</h2>)',
        r'(\s*</section>\s*)(\s*<section class="card">\s*<h2[^>]*>[\s\S]*?Answer đúng[\s\S]*?</h2>)',
    ]

    changed = False
    for pat in patterns:
        new_s, n = re.subn(pat, r'\1' + button_block + r'\2', s, count=1, flags=re.S | re.I)
        if n:
            s = new_s
            changed = True
            break

    # Nếu không tìm được section, chèn ngay sau note đang hiện trong ảnh
    if not changed:
        s = s.replace(
            "Sau khi nhập data answer tổng, bấm lưu. Sau đó 4 ô “Answer đúng” bên dưới sẽ hiện các lựa chọn để chọn cho từng Person.",
            "Sau khi nhập data answer tổng, bấm <b>Save answer tổng</b>. Sau đó 4 ô “Answer đúng” bên dưới sẽ hiện các lựa chọn để chọn cho từng Person."
        )
        s = s.replace(
            "</div>\n</section>",
            "</div>\n" + button_block + "\n</section>",
            1
        )

# 3) Tách form: phần chọn answer đúng bên dưới phải là form save_topic separate
if s.count('<input type="hidden" name="action" value="save_topic">') == 0:
    s = re.sub(
        r'(<section class="card">\s*<h2[^>]*>\s*Choose answer đúng cho 4 person\s*</h2>)',
        r'''</form>

<form method="post">
{% csrf_token %}
<input type="hidden" name="action" value="save_topic">
<input type="hidden" name="title" value="{{ topic.title }}">
<input type="hidden" name="description" value="{{ topic.description }}">
<input type="hidden" name="audio_url" value="{{ topic.audio_url }}">
<textarea name="data_choices" style="display:none">{{ topic.data_choices }}</textarea>

\1''',
        s,
        count=1,
        flags=re.S | re.I
    )

# 4) Edit text nút cuối nếu đang ghi chung chung
s = s.replace(">Save data topics</button>", ">Save answer đúng</button>")

tpl.write_text(s, encoding="utf-8")
print("DA_EP_THEM_NUT_LUU_DAP_AN_TONG")
