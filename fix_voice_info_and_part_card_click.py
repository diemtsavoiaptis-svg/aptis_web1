from pathlib import Path
import re

# ==================================================
# A) FIX TEMPLATE ADMIN MÀY GIỎI: HIỆN topic.voice_info
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
s = tpl.read_text(encoding="utf-8", errors="ignore")

# Đảm bảo textarea voice_info luôn lấy từ database
s = re.sub(
    r'<textarea name="voice_info"[^>]*>[\s\S]*?</textarea>',
    '<textarea name="voice_info" placeholder="Nhập thông tin của voice. Phần này học viên có thể bấm nút để hiển thị hoặc ẩn.">{{ topic.voice_info|default_if_none:"" }}</textarea>',
    s,
    flags=re.S
)

# Nếu chưa có khung Thông tin voice thì thêm lại giữa Lưu đáp án tổng và Chọn đáp án đúng
if 'name="voice_info"' not in s:
    block = r'''
<section class="card voice-info-box">
    <h2 class="voice-info-title">Thông tin của voice</h2>
    <label>Nhập thông tin/ghi chú/giải thích của voice</label>
    <textarea name="voice_info" placeholder="Nhập thông tin của voice. Phần này học viên có thể bấm nút để hiển thị hoặc ẩn.">{{ topic.voice_info|default_if_none:"" }}</textarea>
</section>
'''
    s = s.replace('</section>\n</form>\n\n<form method="post">', '</section>\n' + block + '\n</form>\n\n<form method="post">', 1)

# Đảm bảo CSS khung đẹp
if ".voice-info-box" not in s:
    s = s.replace("</style>", """
.voice-info-box{
    margin-top:16px;
    background:#fff;
    border:1px solid #ffd1dc;
    border-radius:22px;
    padding:18px;
    box-shadow:0 12px 26px rgba(180,0,30,.045);
}
.voice-info-title{
    margin:0 0 12px;
    color:#4a0010;
    font-size:22px;
    font-weight:950;
}
.voice-info-box textarea{
    min-height:190px;
    background:#fff;
}
</style>""")

tpl.write_text(s, encoding="utf-8")


# ==================================================
# B) FIX VIEW: LƯU voice_info KHI BẤM LƯU ĐÁP ÁN TỔNG
# ==================================================
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

if "from django.contrib.auth.decorators import user_passes_test" not in v:
    v = "from django.contrib.auth.decorators import user_passes_test\n" + v
if "from django.shortcuts import render, redirect, get_object_or_404" not in v:
    v = "from django.shortcuts import render, redirect, get_object_or_404\n" + v
if "from django.contrib import messages" not in v:
    v = "from django.contrib import messages\n" + v
if "Part2Topic" not in v or "Part2Voice" not in v:
    if "from .models import" in v:
        v = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic, Part2Voice",
            v,
            count=1
        )
    else:
        v = "from .models import Part2Topic, Part2Voice\n" + v

override = r'''

# ===== FINAL FIX voice_info + correct answers for May Gioi =====
def _is_admin_user_part2_gioi_voice_info_final(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_voice_info_final(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i, question_text=f"Person {i}")

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_options_voice_info_final(topic):
    return [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]


@user_passes_test(_is_admin_user_part2_gioi_voice_info_final)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_info_final(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            voice.question_text = f"Person {voice.order}"
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án tổng và thông tin voice.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_correct_answers":
        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án đúng cho 4 Person.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _gioi_options_voice_info_final(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_info_final(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_options_voice_info_final(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL FIX voice_info + correct answers for May Gioi =====
'''

if "FINAL FIX voice_info + correct answers for May Gioi" not in v:
    v += override

views.write_text(v, encoding="utf-8")


# ==================================================
# C) FIX HỌC VIÊN: NÚT HIỆN / ẨN THÔNG TIN VOICE
# ==================================================
student = Path("templates/core/student_part2_gioi.html")
if student.exists():
    h = student.read_text(encoding="utf-8", errors="ignore")

    if ".voice-toggle-card" not in h:
        h = h.replace("</style>", """
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
.voice-info-content.show{display:block}
</style>""")

    if "toggleVoiceInfo" not in h:
        block = r'''
{% if topic.voice_info %}
<section class="voice-toggle-card">
    <button class="voice-toggle-btn" type="button" onclick="toggleVoiceInfo()">👁 Hiển thị / Ẩn thông tin voice</button>
    <div id="voiceInfoContent" class="voice-info-content">{{ topic.voice_info }}</div>
</section>
{% endif %}
'''
        h = h.replace('</section>\n\n<section class="card">', '</section>\n' + block + '\n<section class="card">', 1)
        h = h.replace("</body>", """<script>
function toggleVoiceInfo(){
    const box = document.getElementById("voiceInfoContent");
    if(box){ box.classList.toggle("show"); }
}
</script>
</body>""")

    student.write_text(h, encoding="utf-8")


# ==================================================
# D) FIX CLICK TOÀN BỘ Ô PART 1-4
# ==================================================
click_js = r'''
<script class="whole-part-card-click-fix">
(function(){
    const adminLinks = {
        "1": "/dashboard/part-1/",
        "2": "/dashboard/part-2/",
        "3": "/dashboard/part-3/",
        "4": "/dashboard/part-4/"
    };

    const studentLinks = {
        "1": "/listening/",
        "2": "/listening/part-2/",
        "3": "/listening/part-3/",
        "4": "/listening/part-4/"
    };

    const isStudent = location.pathname.startsWith("/listening");
    const links = isStudent ? studentLinks : adminLinks;

    function detectPart(text){
        text = (text || "").replace(/\s+/g, " ");
        for(const n of ["1","2","3","4"]){
            const re = new RegExp("(^|\\b)Part\\s*" + n + "(\\b|$)", "i");
            if(re.test(text)) return n;
        }
        return null;
    }

    function findCard(el){
        let cur = el;
        while(cur && cur !== document.body){
            const text = cur.innerText || "";
            const part = detectPart(text);
            if(part){
                const r = cur.getBoundingClientRect();
                if(r.width >= 140 && r.height >= 90){
                    return {card: cur, part: part};
                }
            }
            cur = cur.parentElement;
        }
        return null;
    }

    document.addEventListener("mousemove", function(e){
        const found = findCard(e.target);
        if(found){
            found.card.style.cursor = "pointer";
        }
    }, true);

    document.addEventListener("click", function(e){
        if(e.target.closest("input, textarea, select, label")) return;
        const found = findCard(e.target);
        if(!found) return;
        const url = links[found.part];
        if(url){
            e.preventDefault();
            window.location.href = url;
        }
    }, true);
})();
</script>
'''

for p in Path("templates").rglob("*.html"):
    x = p.read_text(encoding="utf-8", errors="ignore")
    old = x

    if "Part 1" in x or "Part 2" in x or "Part 3" in x or "Part 4" in x:
        x = re.sub(r'<script class="whole-part-card-click-fix">[\s\S]*?</script>', '', x)
        x = x.replace("</body>", click_js + "\n</body>")

    if x != old:
        p.write_text(x, encoding="utf-8")

print("DA_FIX_VOICE_INFO_HIEN_THI_VA_CLICK_TOAN_BO_O_PART")
