from pathlib import Path
import re

# ==================================================
# 1) GHI ĐÈ VIEW MÀY GIỎI: dropdown lấy từ topic.data_choices
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.shortcuts import render, redirect, get_object_or_404",
    "from django.contrib import messages",
]
for imp in imports:
    if imp not in s:
        s = imp + "\n" + s

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

block = r'''

# ===== FINAL FIX: Part 2 May Gioi dropdown options from total data =====
def _is_admin_user_part2_gioi_dropdown(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_4_person_dropdown(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _split_total_answer_options(topic):
    return [
        line.strip()
        for line in (topic.data_choices or "").splitlines()
        if line.strip()
    ]


@user_passes_test(_is_admin_user_part2_gioi_dropdown)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_4_person_dropdown(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.save()

        # Save answer đúng từng person
        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu. Các lựa chọn answer đã được cập nhật từ data answer tổng.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _split_total_answer_options(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_4_person_dropdown(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _split_total_answer_options(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL FIX: Part 2 May Gioi dropdown options from total data =====
'''

# Add block cuối để override các function cũ
if "FINAL FIX: Part 2 May Gioi dropdown options from total data" not in s:
    s += block

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) SỬA TEMPLATE ADMIN: dropdown chắc chắn loop row.options
# ==================================================
tpl = Path("templates/core/admin_part2_gioi_detail.html")
t = tpl.read_text(encoding="utf-8", errors="ignore")

# Edit lại vùng select answer đúng cho từng Person
t = re.sub(
    r'''<select name="voice_\{\{ voice\.id \}\}_correct_data">[\s\S]*?</select>''',
    '''<select name="voice_{{ voice.id }}_correct_data">
                                <option value="">-- Choose answer đúng --</option>
                                {% for option in row.options %}
                                    <option value="{{ option }}" {% if voice.correct_data == option %}selected{% endif %}>
                                        {{ option }}
                                    </option>
                                {% endfor %}
                            </select>''',
    t
)

# Edit note cho rõ
t = t.replace(
    "Nếu chưa thấy lựa chọn, nhập data answer ở cột cuối rồi lưu trước.",
    "Nếu chưa thấy lựa chọn, nhập data answer tổng ở phía trên, mỗi answer một dòng, rồi bấm Save."
)

t = t.replace(
    "Person {{ voice.order }} chọn 1 trong 4 lựa chọn.",
    "Person {{ voice.order }} chọn 1 trong các data answer tổng."
)

tpl.write_text(t, encoding="utf-8")


# ==================================================
# 3) SỬA TEMPLATE HỌC VIÊN: dropdown cũng lấy row.options
# ==================================================
student = Path("templates/core/student_part2_gioi.html")
if student.exists():
    h = student.read_text(encoding="utf-8", errors="ignore")

    h = re.sub(
        r'''<select>[\s\S]*?</select>''',
        '''<select>
                    <option>-- Select an answer --</option>
                    {% for option in row.options %}
                        <option>{{ option }}</option>
                    {% endfor %}
                </select>''',
        h
    )

    student.write_text(h, encoding="utf-8")


print("DA_SUA_DROPDOWN_DOC_TU_DU_LIEU_DAP_AN_TONG")
