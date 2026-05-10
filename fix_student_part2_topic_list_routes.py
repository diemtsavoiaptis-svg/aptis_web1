from pathlib import Path
import re

# ==================================================
# 1) Sửa views.py: thêm view danh sách chủ đề học viên
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.shortcuts import render, get_object_or_404",
]
for imp in imports:
    if imp not in s:
        s = imp + "\n" + s

if "Part2Topic" not in s:
    if "from .models import" in s:
        s = re.sub(
            r"from \.models import ([^\n]+)",
            lambda m: "from .models import " + m.group(1).rstrip() + ", Part2Topic",
            s,
            count=1
        )
    else:
        s = "from .models import Part2Topic\n" + s

block = r'''

# ===== Fix student Part 2 topic list routes =====
def student_part2_gioi_topics(request):
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày giỏi",
        "topics": topics,
        "back_url": "/listening/part-2/",
        "topic_url_prefix": "/listening/part-2/may-gioi/",
    })


def student_part2_kem_topics(request):
    topics = Part2Topic.objects.filter(version="kem").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày kém",
        "topics": topics,
        "back_url": "/listening/part-2/",
        "topic_url_prefix": "/listening/part-2/may-kem/",
    })


# Alias phòng khi code cũ gọi may-dot
def student_part2_dot_topics(request):
    return student_part2_kem_topics(request)
# ===== End fix student Part 2 topic list routes =====
'''

if "Fix student Part 2 topic list routes" not in s:
    s += block

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) Sửa urls.py: thêm route danh sách TRƯỚC route có <int:topic_id>
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

# Xóa các route trùng may-gioi/may-kem list nếu có để thêm lại đúng vị trí
u = re.sub(r'\s*path\("listening/part-2/may-gioi/",\s*views\.[^,]+,\s*name="[^"]+"\),\n?', "\n", u)
u = re.sub(r'\s*path\("listening/part-2/may-kem/",\s*views\.[^,]+,\s*name="[^"]+"\),\n?', "\n", u)
u = re.sub(r'\s*path\("listening/part-2/may-dot/",\s*views\.[^,]+,\s*name="[^"]+"\),\n?', "\n", u)

new_routes = '''    path("listening/part-2/may-gioi/", views.student_part2_gioi_topics, name="student_part2_gioi_topics"),
    path("listening/part-2/may-kem/", views.student_part2_kem_topics, name="student_part2_kem_topics"),
    path("listening/part-2/may-dot/", views.student_part2_dot_topics, name="student_part2_dot_topics"),
'''

# Chèn ngay đầu urlpatterns để list route được bắt trước detail route
u = re.sub(
    r"urlpatterns\s*=\s*\[",
    "urlpatterns = [\n" + new_routes,
    u,
    count=1
)

# Sửa link may-dot cũ thành may-kem trong templates sau
urls.write_text(u, encoding="utf-8")


# ==================================================
# 3) Đảm bảo template danh sách chủ đề học viên tồn tại
# ==================================================
tpl = Path("templates/core/student_part2_topic_list.html")
tpl.parent.mkdir(parents=True, exist_ok=True)

tpl.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Part 2 - {{ version_title }}</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
:root{--red:#e60023;--red2:#ff5f76;--dark:#3f0011;--line:#ffd1dc;--muted:#667085}
*{box-sizing:border-box}
body{
    margin:0;
    min-height:100vh;
    background:linear-gradient(135deg,#fffafa,#fff0f4 48%,#fff7f9);
    font-family:"Segoe UI",Tahoma,Arial,sans-serif;
    color:var(--dark);
}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px}
.hero,.topic{
    background:white;
    border:1px solid var(--line);
    border-radius:28px;
    padding:26px;
    box-shadow:0 18px 44px rgba(180,0,30,.07);
}
h1{margin:0;font-size:44px;letter-spacing:-.05em}
.desc{margin-top:10px;color:var(--muted);font-size:17px;line-height:1.65;font-weight:650}
.back{
    display:inline-flex;
    margin-top:16px;
    min-height:44px;
    padding:0 16px;
    border-radius:999px;
    background:#fff1f4;
    color:#8a0015;
    border:1px solid var(--line);
    text-decoration:none;
    font-weight:950;
}
.grid{margin-top:20px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.topic{text-decoration:none;color:inherit;display:block;transition:.15s ease}
.topic:hover{transform:translateY(-3px);box-shadow:0 22px 48px rgba(180,0,30,.11)}
.topic h2{margin:0;font-size:23px;color:#4a0010;letter-spacing:-.03em}
.topic p{color:var(--muted);line-height:1.55}
@media(max-width:920px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">
<section class="hero">
    <h1>Part 2 - {{ version_title }}</h1>
    <div class="desc">Chọn chủ đề để bắt đầu làm bài.</div>
    <a class="back" href="{{ back_url }}">← Quay lại chọn phiên bản</a>
</section>

<section class="grid">
{% for topic in topics %}
<a class="topic" href="{{ topic_url_prefix }}{{ topic.id }}/">
    <h2>{{ topic.title }}</h2>
    <p>{{ topic.description|default:"Chủ đề luyện nghe" }}</p>
</a>
{% empty %}
<div class="topic">
    <h2>Chưa có chủ đề</h2>
    <p>Admin chưa nhập dữ liệu cho phiên bản này.</p>
</div>
{% endfor %}
</section>
</main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 4) Sửa link trong template chọn phiên bản nếu bị may-dot
# ==================================================
for p in Path("templates").rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    old = text
    text = text.replace('/listening/part-2/may-dot/', '/listening/part-2/may-kem/')
    if text != old:
        p.write_text(text, encoding="utf-8")
        print("DA_SUA_LINK:", p)

print("DA_FIX_ROUTE_DANH_SACH_CHU_DE_HOC_VIEN_PART2")
