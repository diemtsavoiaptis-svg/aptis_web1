from pathlib import Path
import re

# ==================================================
# 1) Tạo template quản lý admin cho Part 2/3/4: chỉ là khung chờ dữ liệu
# ==================================================
admin_tpl = Path("templates/core/admin_part_placeholder.html")
admin_tpl.parent.mkdir(parents=True, exist_ok=True)

admin_tpl.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Quản lý {{ part_title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
    <style>
        body{
            margin:0;
            min-height:100vh;
            padding:34px;
            background:linear-gradient(135deg,#fffafa,#fff1f4);
            color:#3f0011;
            font-family:"Segoe UI",Tahoma,Arial,sans-serif;
        }
        .card{
            max-width:1100px;
            margin:auto;
            background:white;
            border:1px solid #ffd1dc;
            border-radius:30px;
            padding:36px;
            box-shadow:0 20px 46px rgba(180,0,30,.08);
        }
        .badge{
            width:72px;
            height:72px;
            border-radius:22px;
            background:linear-gradient(135deg,#e60023,#ff5f76);
            color:white;
            display:grid;
            place-items:center;
            font-size:34px;
            font-weight:950;
        }
        h1{
            font-size:48px;
            margin:22px 0 12px;
            letter-spacing:-.04em;
        }
        p{
            font-size:18px;
            color:#667085;
            line-height:1.7;
            max-width:760px;
        }
        .note{
            margin-top:22px;
            padding:22px;
            border-radius:22px;
            border:1px dashed #ff9cac;
            background:#fffafa;
            color:#8a0015;
            font-weight:800;
            line-height:1.7;
        }
        .actions{
            display:flex;
            gap:12px;
            flex-wrap:wrap;
            margin-top:24px;
        }
        a{
            min-height:48px;
            padding:0 20px;
            border-radius:999px;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            text-decoration:none;
            font-weight:950;
        }
        .primary{
            background:linear-gradient(135deg,#e60023,#ff5f76);
            color:white;
        }
        .light{
            background:#fff1f4;
            color:#8a0015;
            border:1px solid #ffd1dc;
        }
    </style>
</head>
<body>
    <section class="card">
        <div class="badge">{{ part_number }}</div>
        <h1>Quản lý {{ part_title }}</h1>
        <p>{{ part_desc }}</p>

        <div class="note">
            Đây là khu vực quản lý dữ liệu cho admin. Giao diện học viên của {{ part_title }} sẽ nằm riêng ở đường dẫn làm bài, không đặt trong trang quản lý dữ liệu.
        </div>

        <div class="actions">
            <a class="primary" href="/dashboard/listening-parts/">← Quay lại chọn Part</a>
            <a class="light" href="/listening/part-{{ part_number }}/">Xem giao diện học viên</a>
        </div>
    </section>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 2) Sửa views: dashboard/part-* là admin, listening/part-* là học viên
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

# Xóa các block view Part 2/3/4 cũ nếu có dạng đơn giản
s = re.sub(
    r"\n?# ===== Listening Part 2 preview/interface =====[\s\S]*?# ===== End Listening Part 2 preview/interface =====\n?",
    "\n",
    s
)
s = re.sub(
    r"\n?# ===== Listening Part 2 interface =====[\s\S]*?# ===== End Listening Part 2 interface =====\n?",
    "\n",
    s
)
s = re.sub(
    r"\n?# ===== Listening Part 3 placeholder =====[\s\S]*?# ===== End Listening Part 3 placeholder =====\n?",
    "\n",
    s
)
s = re.sub(
    r"\n?# ===== Listening Part 4 placeholder =====[\s\S]*?# ===== End Listening Part 4 placeholder =====\n?",
    "\n",
    s
)

# Xóa def cũ nếu script trước đã thêm
s = re.sub(
    r"(?ms)^def admin_part2_questions\(request\):\s*\n    return render\(request, .*?\)\s*\n",
    "",
    s
)
s = re.sub(
    r"(?ms)^def admin_part3_questions\(request\):\s*\n    return render\(request, .*?\n    \}\)\s*\n",
    "",
    s
)
s = re.sub(
    r"(?ms)^def admin_part4_questions\(request\):\s*\n    return render\(request, .*?\n    \}\)\s*\n",
    "",
    s
)

block = r'''

# ===== Admin management placeholders for Listening Parts =====
def admin_part2_questions(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 2,
        "part_title": "Part 2",
        "part_desc": "Part 2 sẽ là khu vực quản lý topic, 4 voice, pool đáp án A-B-C-D, đáp án đúng và transcript. Hiện chưa nhập dữ liệu thật.",
    })

def admin_part3_questions(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Part 3 đã mở khu vực quản lý dữ liệu. Hiện chưa có dữ liệu thật, sẽ thiết kế chi tiết sau.",
    })

def admin_part4_questions(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Part 4 đã mở khu vực quản lý dữ liệu. Hiện chưa có dữ liệu thật, sẽ thiết kế chi tiết sau.",
    })
# ===== End admin management placeholders =====


# ===== Student listening interfaces =====
def student_part2_page(request):
    return render(request, "core/listening_part2.html")

def student_part3_page(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Giao diện học viên Part 3 hiện chưa có dữ liệu.",
    })

def student_part4_page(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Giao diện học viên Part 4 hiện chưa có dữ liệu.",
    })
# ===== End student listening interfaces =====
'''

if "def student_part2_page(request):" not in s:
    s += block

views.write_text(s, encoding="utf-8")


# ==================================================
# 3) Sửa urls: thêm route học viên riêng
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

needed_routes = [
    ('dashboard/part-2/', '    path("dashboard/part-2/", views.admin_part2_questions, name="admin_part2_questions"),'),
    ('dashboard/part-3/', '    path("dashboard/part-3/", views.admin_part3_questions, name="admin_part3_questions"),'),
    ('dashboard/part-4/', '    path("dashboard/part-4/", views.admin_part4_questions, name="admin_part4_questions"),'),
    ('listening/part-2/', '    path("listening/part-2/", views.student_part2_page, name="student_part2"),'),
    ('listening/part-3/', '    path("listening/part-3/", views.student_part3_page, name="student_part3"),'),
    ('listening/part-4/', '    path("listening/part-4/", views.student_part4_page, name="student_part4"),'),
]

for key, route in needed_routes:
    if key not in u:
        u = re.sub(
            r"urlpatterns\s*=\s*\[",
            "urlpatterns = [\n" + route,
            u,
            count=1
        )

u = u.replace('name="admin_part1_questions"),    path("listening/"', 'name="admin_part1_questions"),\n    path("listening/"')
urls.write_text(u, encoding="utf-8")


# ==================================================
# 4) Sửa nút thoát của giao diện học viên Part 2 về trang listening
# ==================================================
part2 = Path("templates/core/listening_part2.html")
if part2.exists():
    p2 = part2.read_text(encoding="utf-8", errors="ignore")
    p2 = p2.replace('href="/dashboard/listening-parts/"', 'href="/listening/"')
    p2 = p2.replace("← Thoát", "← Thoát bài")
    part2.write_text(p2, encoding="utf-8")


# ==================================================
# 5) Sửa trang chọn Part admin: nút Part 2/3/4 mở trang quản lý admin, không phải giao diện học viên
# ==================================================
for p in Path("templates").rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if "Chọn Part cần quản lý" not in text and "Khu vực quản lý dữ liệu cho Part 2" not in text:
        continue

    old = text
    text = text.replace('href="/listening/part-2/"', 'href="/dashboard/part-2/"')
    text = text.replace('href="/listening/part-3/"', 'href="/dashboard/part-3/"')
    text = text.replace('href="/listening/part-4/"', 'href="/dashboard/part-4/"')

    text = text.replace("Part 2 gồm 1 chủ đề lớn, 4 voice thảo luận và pool đáp án A-B-C-D.", "Khu vực quản lý dữ liệu cho Part 2. Chưa có dữ liệu thật.")
    text = text.replace("Part 3 hiện chưa có dữ liệu. Đã mở khung để thiết kế sau.", "Khu vực quản lý dữ liệu cho Part 3. Chưa có dữ liệu thật.")
    text = text.replace("Part 4 hiện chưa có dữ liệu. Đã mở khung để thiết kế sau.", "Khu vực quản lý dữ liệu cho Part 4. Chưa có dữ liệu thật.")

    if text != old:
        p.write_text(text, encoding="utf-8")
        print("DA_SUA_TRANG_CHON_PART_ADMIN:", p)

print("DA_TACH_LAI_ADMIN_PART_VA_GIAO_DIEN_HOC_VIEN")
