from pathlib import Path
import re

# ==================================================
# 1) Thêm field voice_info vào Part2Topic
# ==================================================
models = Path("core/models.py")
s = models.read_text(encoding="utf-8", errors="ignore")

topic_block_match = re.search(r"class\s+Part2Topic\(models\.Model\):[\s\S]*?(?=\nclass\s+Part2Voice|\Z)", s)
if not topic_block_match:
    raise SystemExit("KHONG_TIM_THAY_CLASS_Part2Topic")

topic_block = topic_block_match.group(0)

if "voice_info" not in topic_block:
    if "audio_url" in topic_block:
        s = re.sub(
            r'(audio_url\s*=\s*models\.URLField\([^\n]+\)\n)',
            r'\1    voice_info = models.TextField("Thông tin của voice", blank=True)\n',
            s,
            count=1
        )
    else:
        s = re.sub(
            r'(description\s*=\s*models\.TextField\([^\n]+\)\n)',
            r'\1    voice_info = models.TextField("Thông tin của voice", blank=True)\n',
            s,
            count=1
        )

models.write_text(s, encoding="utf-8")


# ==================================================
# 2) Sửa view Mày giỏi: lưu voice_info
# ==================================================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

# Lưu trong action save_total_answers
v = v.replace(
    'topic.data_choices = request.POST.get("data_choices", "").strip()\n        topic.save()',
    'topic.data_choices = request.POST.get("data_choices", "").strip()\n        topic.voice_info = request.POST.get("voice_info", "").strip()\n        topic.save()',
    1
)

# Nếu có nhiều block override, thay tất cả các chỗ save_total_answers còn lại có data_choices
v = re.sub(
    r'(topic\.data_choices\s*=\s*request\.POST\.get\("data_choices", ""\)\.strip\(\)\n)(\s*topic\.save\(\))',
    r'\1        topic.voice_info = request.POST.get("voice_info", "").strip()\n\2',
    v
)

# Khi save_correct_answers, giữ lại voice_info nếu form có gửi
v = re.sub(
    r'(if request\.method == "POST" and request\.POST\.get\("action"\) == "save_correct_answers":[\s\S]{0,250})',
    lambda m: m.group(1) if "voice_info" in m.group(1) else m.group(1),
    v
)

views.write_text(v, encoding="utf-8")


# ==================================================
# 3) Sửa template admin: thêm bảng trắng "Thông tin của voice"
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# Thêm CSS cho bảng thông tin voice
if ".voice-info-box" not in t:
    t = t.replace(
        "</style>",
        """
.voice-info-box{
    margin-top:16px;
    background:#ffffff;
    border:1px solid #ffd1dc;
    border-radius:22px;
    padding:18px;
    box-shadow:0 12px 26px rgba(180,0,30,.045);
}
.voice-info-box textarea{
    min-height:170px;
    background:#fff;
}
.voice-info-title{
    margin:0 0 12px;
    color:#4a0010;
    font-size:22px;
    font-weight:950;
}
</style>"""
    )

# Chèn input voice_info vào form save_total_answers ngay sau nút Lưu đáp án tổng
if 'name="voice_info"' not in t:
    insert_block = r'''
</section>

<section class="card voice-info-box">
    <h2 class="voice-info-title">Thông tin của voice</h2>
    <label>Nhập thông tin/ghi chú/giải thích của voice</label>
    <textarea name="voice_info" placeholder="Nhập thông tin của voice. Phần này học viên có thể bấm nút để hiển thị hoặc ẩn.">{{ topic.voice_info }}</textarea>
</section>
'''
    t = t.replace(
        '</section>\n</form>\n\n<form method="post">',
        insert_block + '\n</form>\n\n<form method="post">',
        1
    )

# Form lưu đáp án đúng cần giữ hidden voice_info để không mất khi submit nếu view có nhận
if '<textarea name="voice_info" style="display:none">' not in t:
    t = t.replace(
        '<input type="hidden" name="action" value="save_correct_answers">',
        '<input type="hidden" name="action" value="save_correct_answers">\n<textarea name="voice_info" style="display:none">{{ topic.voice_info }}</textarea>',
        1
    )

tpl.write_text(t, encoding="utf-8")


# ==================================================
# 4) Sửa template học viên: thêm nút hiển thị/ẩn thông tin voice
# ==================================================
student = Path("templates/core/student_part2_gioi.html")
h = student.read_text(encoding="utf-8", errors="ignore")

if ".voice-toggle-card" not in h:
    h = h.replace(
        "</style>",
        """
.voice-toggle-card{
    margin-top:16px;
    background:white;
    border:1px solid #ffd1dc;
    border-radius:24px;
    padding:20px;
    box-shadow:0 18px 40px rgba(180,0,30,.07);
}
.voice-toggle-btn{
    width:100%;
    min-height:52px;
    border:0;
    border-radius:16px;
    background:linear-gradient(135deg,#e60023,#ff5f76);
    color:white;
    font-size:18px;
    font-weight:950;
    cursor:pointer;
    box-shadow:0 14px 28px rgba(230,0,35,.16);
}
.voice-info-content{
    display:none;
    margin-top:16px;
    padding:18px;
    border-radius:18px;
    border:1px solid #ffd1dc;
    background:#fffafa;
    color:#3f0011;
    font-size:17px;
    line-height:1.75;
    white-space:pre-wrap;
    font-weight:650;
}
.voice-info-content.show{
    display:block;
}
</style>"""
    )

if "toggleVoiceInfo" not in h:
    voice_block = r'''
{% if topic.voice_info %}
<section class="voice-toggle-card">
    <button class="voice-toggle-btn" type="button" onclick="toggleVoiceInfo()">
        👁 Hiển thị / Ẩn thông tin voice
    </button>
    <div id="voiceInfoContent" class="voice-info-content">{{ topic.voice_info }}</div>
</section>
{% endif %}
'''
    # Chèn sau card audio/topic đầu tiên, trước danh sách person
    h = h.replace(
        '</section>\n\n<section class="card">',
        '</section>\n' + voice_block + '\n<section class="card">',
        1
    )

    h = h.replace(
        "</body>",
        """<script>
function toggleVoiceInfo(){
    const box = document.getElementById("voiceInfoContent");
    if(box){
        box.classList.toggle("show");
    }
}
</script>
</body>"""
    )

student.write_text(h, encoding="utf-8")

print("DA_THEM_THONG_TIN_VOICE_ADMIN_VA_NUT_HIEN_AN_CHO_HOC_VIEN")
