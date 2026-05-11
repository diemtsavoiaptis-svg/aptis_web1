from pathlib import Path
import re

# 1) Đảm bảo URL Part 2/3/4 tồn tại
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

routes = [
    ('dashboard/part-2/', '    path("dashboard/part-2/", views.admin_part2_questions, name="admin_part2_questions"),'),
    ('dashboard/part-3/', '    path("dashboard/part-3/", views.admin_part3_questions, name="admin_part3_questions"),'),
    ('dashboard/part-4/', '    path("dashboard/part-4/", views.admin_part4_questions, name="admin_part4_questions"),'),
]

for key, route in routes:
    if key not in u:
        u = re.sub(r"urlpatterns\s*=\s*\[", "urlpatterns = [\n" + route, u, count=1)

u = u.replace('name="admin_part1_questions"),    path("listening/"', 'name="admin_part1_questions"),\n    path("listening/"')
urls.write_text(u, encoding="utf-8")


# 2) Đảm bảo view Part 2/3/4 tồn tại
views = Path("core/views.py")
v = views.read_text(encoding="utf-8", errors="ignore")

if "def admin_part2_questions(request):" not in v:
    v += '''

def admin_part2_questions(request):
    return render(request, "core/listening_part2.html")
'''

if "def admin_part3_questions(request):" not in v:
    v += '''

def admin_part3_questions(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Part 3 currently has no data. Đã mở khung để thiết kế sau.",
    })
'''

if "def admin_part4_questions(request):" not in v:
    v += '''

def admin_part4_questions(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Part 4 currently has no data. Đã mở khung để thiết kế sau.",
    })
'''

views.write_text(v, encoding="utf-8")


# 3) Tạo trang Part 2 nếu thiếu
part2 = Path("templates/core/listening_part2.html")
part2.parent.mkdir(parents=True, exist_ok=True)
if not part2.exists():
    part2.write_text("""{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Part 2</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
body{margin:0;padding:26px;background:linear-gradient(135deg,#fffafa,#fff1f4);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:#3f0011}
.wrap{max-width:1200px;margin:auto}
.top{border-left:4px solid #e60023;background:#fff1f4;border-radius:0 14px 14px 0;padding:14px 18px;font-weight:900;color:#7a0010}
.topic{display:inline-flex;margin-top:18px;padding:12px 18px;border:1px solid #ffd1dc;border-radius:999px;background:white;font-weight:900}
.pool,.voice{margin-top:16px;border:1px solid #ffd1dc;border-radius:20px;background:white;padding:18px;box-shadow:0 18px 40px rgba(180,0,30,.06)}
.pool-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}
.opt{padding:13px;border:1px solid #ffd1dc;border-radius:14px;background:#fffafa;font-weight:800}
.voice{display:grid;grid-template-columns:1fr 180px;gap:14px;align-items:center}
.badge{display:inline-grid;place-items:center;width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#e60023,#ff5f76);color:white;font-weight:950;margin-right:10px}
.audio{margin-top:12px;background:#fff1f4;border-radius:14px;padding:16px;font-weight:800}
select{height:48px;border-radius:14px;border:1px dashed #ff9cac;padding:0 12px}
@media(max-width:800px){.pool-grid{grid-template-columns:1fr}.voice{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="wrap">
<div class="top">Part 2</div>
<div class="topic">🏷 TOPIC: When they like listening to music</div>
<section class="pool">
<b>☰ Pool answer</b>
<div class="pool-grid">
<div class="opt">A. To relax</div>
<div class="opt">B. While studying</div>
<div class="opt">C. While singing</div>
<div class="opt">D. After waking up</div>
</div>
</section>
{% for i in "1234" %}
<section class="voice">
<div>
<div><span class="badge">{{ forloop.counter }}</span><b>Câu {{ forloop.counter }}</b></div>
<div class="audio">▶ Audio voice {{ forloop.counter }} — data thật sẽ nhập sau</div>
</div>
<select>
<option>Choose answer...</option>
<option>A</option><option>B</option><option>C</option><option>D</option>
</select>
</section>
{% endfor %}
</main>
</body>
</html>
""", encoding="utf-8")


# 4) Tạo placeholder Part 3/4 nếu thiếu
placeholder = Path("templates/core/listening_part_placeholder.html")
if not placeholder.exists():
    placeholder.write_text("""{% load static %}
<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{{ part_title }}</title>
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
body{margin:0;min-height:100vh;padding:34px;background:linear-gradient(135deg,#fffafa,#fff1f4);font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:#3f0011}
.card{max-width:1000px;margin:auto;background:white;border:1px solid #ffd1dc;border-radius:30px;padding:36px;box-shadow:0 20px 46px rgba(180,0,30,.08)}
.badge{width:72px;height:72px;border-radius:22px;background:linear-gradient(135deg,#e60023,#ff5f76);color:white;display:grid;place-items:center;font-size:34px;font-weight:950}
h1{font-size:58px;margin:20px 0 10px}
p{font-size:20px;color:#667085;line-height:1.7}
a{display:inline-flex;margin-top:20px;background:linear-gradient(135deg,#e60023,#ff5f76);color:white;text-decoration:none;padding:15px 22px;border-radius:16px;font-weight:900}
</style>
</head>
<body>
<section class="card">
<div class="badge">{{ part_number }}</div>
<h1>{{ part_title }}</h1>
<p>{{ part_desc }}</p>
<p>Phần này chưa có data. Khi bắt đầu làm, mình sẽ thiết kế chi tiết sau và không ảnh hưởng Part 1.</p>
<a href="/dashboard/listening-parts/">Back chọn Part</a>
</section>
</body>
</html>
""", encoding="utf-8")


# 5) Tìm đúng template chọn Part đang chứa text cũ và sửa trực tiếp
matched = []
for p in Path("templates").rglob("*.html"):
    s = p.read_text(encoding="utf-8", errors="ignore")
    if "Khu vực manage data cho Part 2" in s or "Choose Part to Manage" in s:
        matched.append(p)

for p in matched:
    s = p.read_text(encoding="utf-8", errors="ignore")
    old = s

    s = s.replace(
        "Khu vực manage data cho Part 2. Có thể tiếp tục mở rộng interface chi tiết sau khi hoàn thiện Part 1.",
        "Part 2 gồm 1 topics lớn, 4 voice thảo luận và pool answer A-B-C-D."
    )
    s = s.replace(
        "Khu vực manage data cho Part 3. Có thể tiếp tục mở rộng interface chi tiết sau khi hoàn thiện Part 1.",
        "Part 3 currently has no data. Đã mở khung để thiết kế sau."
    )
    s = s.replace(
        "Khu vực manage data cho Part 4. Có thể tiếp tục mở rộng interface chi tiết sau khi hoàn thiện Part 1.",
        "Part 4 currently has no data. Đã mở khung để thiết kế sau."
    )

    # Đổi nhãn
    s = s.replace("Sẵn sàng thiết kế", "Đã mở khung")
    s = s.replace("Sắp mở", "Mở Part")

    # Edit separate các nút theo Part bằng cách tìm card chứa Part n
    def fix_card_link(text, part):
        url = f"/dashboard/part-{part}/"
        # Card dạng article/div chứa Part n: thêm onclick vào toàn card nếu chưa có
        text = re.sub(
            rf'(<(?:article|div)[^>]*class="[^"]*(?:part-card|card)[^"]*"[^>]*)(>[\s\S]{{0,1600}}?Part {part}[\s\S]{{0,1600}}?</(?:article|div)>)',
            lambda m: (m.group(1) if "onclick=" in m.group(1) else m.group(1) + f' onclick="window.location.href=\'{url}\'" style="cursor:pointer"') + m.group(2),
            text,
            count=1,
            flags=re.I
        )

        # Nút trong trang
        text = re.sub(
            rf'(<button[^>]*)(>\s*Mở Part(?:\s*{part})?\s*</button>)',
            lambda m: (m.group(1) if "onclick=" in m.group(1) else m.group(1) + f' onclick="window.location.href=\'{url}\'"') + f'>Mở Part {part}</button>',
            text,
            flags=re.I
        )

        # Link cũ nếu có
        text = re.sub(
            rf'<a([^>]*)>\s*Mở Part(?:\s*{part})?\s*</a>',
            f'<a\\1 href="{url}">Mở Part {part}</a>',
            text,
            flags=re.I
        )
        return text

    for part in [2, 3, 4]:
        s = fix_card_link(s, part)

    # Nếu chữ bị thành "Mở Part" chung thì sửa theo thứ tự xuất hiện Part 2/3/4
    s = re.sub(r'(Part 2[\s\S]{0,900}?)Mở Part(?!\s*2)', r'\1Open Part 2', s, count=1)
    s = re.sub(r'(Part 3[\s\S]{0,900}?)Mở Part(?!\s*3)', r'\1Open Part 3', s, count=1)
    s = re.sub(r'(Part 4[\s\S]{0,900}?)Mở Part(?!\s*4)', r'\1Open Part 4', s, count=1)

    if s != old:
        p.write_text(s, encoding="utf-8")
        print("DA_SUA_TEMPLATE:", p)

print("CAC_FILE_CHUA_TRANG_CHON_PART:", [str(x) for x in matched])
print("DA_MO_LINK_PART_2_3_4")
