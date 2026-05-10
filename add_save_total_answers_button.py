from pathlib import Path
import re

# ==================================================
# 1) Sửa views.py: thêm action lưu riêng "Dữ liệu đáp án tổng"
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

# Tìm function admin_part2_gioi_detail cuối cùng và chèn xử lý save_total_answers
marker = '''    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_topic":'''

replacement = '''    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.save()

        for voice in voices:
            voice.audio_url = topic.audio_url
            voice.question_text = f"Person {voice.order}"
            voice.save()

        messages.success(request, "Đã lưu dữ liệu đáp án tổng. Bây giờ bạn có thể chọn đáp án đúng cho từng Person.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_topic":'''

# Thay lần cuối để tránh đụng các block cũ
idx = s.rfind(marker)
if idx != -1 and "save_total_answers" not in s[idx:idx+1500]:
    s = s[:idx] + replacement + s[idx+len(marker):]

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) Sửa template admin Mày giỏi:
#    - Thêm nút Lưu đáp án tổng ngay dưới ô dữ liệu tổng
#    - Tách form lưu đáp án đúng bên dưới
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# Đảm bảo action form chính ban đầu là save_total_answers cho phần trên
t = t.replace(
    '<input type="hidden" name="action" value="save_topic">',
    '<input type="hidden" name="action" value="save_total_answers">',
    1
)

# Thêm nút Lưu đáp án tổng sau note của dữ liệu tổng nếu chưa có
if "Lưu đáp án tổng" not in t:
    old_note = '''<div class="note">
        Sau khi nhập dữ liệu đáp án tổng, bấm lưu. Sau đó 4 ô “Đáp án đúng” bên dưới sẽ hiện 4 lựa chọn để chọn cho từng Person.
    </div>
</section>'''

    new_note = '''<div class="note">
        Sau khi nhập dữ liệu đáp án tổng, bấm <b>Lưu đáp án tổng</b>. Sau đó 4 ô “Đáp án đúng” bên dưới sẽ hiện các lựa chọn để chọn cho từng Person.
    </div>

    <div class="actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Lưu đáp án tổng</button>
    </div>
</section>'''

    t = t.replace(old_note, new_note)

# Nếu text note khác thì chèn theo textarea data_choices
if "Lưu đáp án tổng" not in t:
    t = t.replace(
        '</section>\n\n<section class="card">\n    <h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>',
        '''    <div class="note">
        Sau khi nhập dữ liệu đáp án tổng, bấm <b>Lưu đáp án tổng</b>. Sau đó 4 ô “Đáp án đúng” bên dưới sẽ hiện các lựa chọn để chọn cho từng Person.
    </div>

    <div class="actions" style="justify-content:flex-end;margin-top:16px">
        <button class="btn" type="submit">Lưu đáp án tổng</button>
    </div>
</section>

<form method="post">
{% csrf_token %}
<input type="hidden" name="action" value="save_topic">

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>''',
        1
    )

# Nếu đã có form nhưng chưa tách phần dưới, tách trước section "Chọn đáp án đúng"
if '<h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>' in t and t.count('<form method="post">') < 2:
    t = t.replace(
        '<section class="card">\n    <h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>',
        '''</form>

<form method="post">
{% csrf_token %}
<input type="hidden" name="action" value="save_topic">

<section class="card">
    <h2 style="margin:0 0 8px;color:#4a0010">Chọn đáp án đúng cho 4 person</h2>''',
        1
    )

# Cần gửi lại dữ liệu topic khi bấm lưu đáp án đúng để không mất dữ liệu
hidden_fields = '''<input type="hidden" name="title" value="{{ topic.title }}">
<input type="hidden" name="description" value="{{ topic.description }}">
<input type="hidden" name="audio_url" value="{{ topic.audio_url }}">
<textarea name="data_choices" style="display:none">{{ topic.data_choices }}</textarea>
'''

if hidden_fields not in t:
    t = t.replace(
        '<input type="hidden" name="action" value="save_topic">',
        '<input type="hidden" name="action" value="save_topic">\n' + hidden_fields,
        1
    )

# Sửa note dưới dropdown
t = t.replace(
    "Nếu chưa thấy lựa chọn, nhập dữ liệu đáp án tổng ở phía trên, mỗi đáp án một dòng, rồi bấm Lưu.",
    "Nếu chưa thấy lựa chọn, nhập dữ liệu đáp án tổng ở phía trên rồi bấm Lưu đáp án tổng."
)

# Đảm bảo nút cuối vẫn là lưu đáp án đúng
t = t.replace("Lưu dữ liệu chủ đề</button>", "Lưu đáp án đúng</button>")

tpl.write_text(t, encoding="utf-8")

print("DA_THEM_NUT_LUU_DAP_AN_TONG_CHO_MAY_GIOI")
