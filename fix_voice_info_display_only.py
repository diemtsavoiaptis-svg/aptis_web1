from pathlib import Path
import re

tpl = Path("templates/core/admin_part2_gioi_detail.html")
s = tpl.read_text(encoding="utf-8", errors="ignore")

# Xóa toàn bộ block Thông tin voice cũ
s = re.sub(
    r'\s*<section class="card voice-info-box">[\s\S]*?</section>\s*',
    '\n',
    s,
    flags=re.S
)

# Block mới: chỉ hiển thị nội dung đã lưu của topic
voice_block = r'''
<section class="card voice-info-box">
    <h2 class="voice-info-title">Nội dung voice / Transcript</h2>

    {% if topic.voice_info %}
        <div class="voice-info-display">{{ topic.voice_info }}</div>
    {% else %}
        <div class="voice-info-empty">
            Chưa có transcript cho topic này. Nếu đã chạy lệnh nhập 12 topic mà vẫn trống, kiểm tra lại dữ liệu topic trong database.
        </div>
    {% endif %}

    <input type="hidden" name="voice_info" value="{{ topic.voice_info|default_if_none:'' }}">
</section>
'''

# Chèn vào giữa nút Lưu đáp án tổng và Chọn đáp án đúng
s = s.replace(
    '</section>\n</form>\n\n<form method="post">',
    '</section>\n' + voice_block + '\n</form>\n\n<form method="post">',
    1
)

# CSS hiển thị đẹp, không còn cuộn trong textarea
css = r'''
.voice-info-box{
    margin-top:16px;
    background:#fff;
    border:1px solid #ffd1dc;
    border-radius:22px;
    padding:20px;
    box-shadow:0 12px 26px rgba(180,0,30,.045);
}
.voice-info-title{
    margin:0 0 14px;
    color:#4a0010;
    font-size:24px;
    font-weight:950;
}
.voice-info-display{
    width:100%;
    min-height:180px;
    padding:18px 20px;
    border:1px solid #ffd1dc;
    border-radius:18px;
    background:#fffafa;
    color:#111827;
    font-size:16px;
    line-height:1.75;
    white-space:pre-wrap;
    font-weight:600;
}
.voice-info-empty{
    padding:18px 20px;
    border:1px dashed #ff9cac;
    border-radius:18px;
    background:#fff6f8;
    color:#9f0018;
    font-weight:850;
}
'''

# Gỡ các CSS cũ của voice-info nếu có rồi thêm CSS mới
s = re.sub(r'\.voice-info-box\{[\s\S]*?\.unlock-voice-btn\{[\s\S]*?\}', '', s, flags=re.S)
s = s.replace("</style>", css + "\n</style>")

tpl.write_text(s, encoding="utf-8")

print("DA_DOI_THONG_TIN_VOICE_THANH_KHUNG_HIEN_THI_TRANSCRIPT")
