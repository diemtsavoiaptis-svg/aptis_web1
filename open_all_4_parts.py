from pathlib import Path
import re

# ==================================================
# 1) Đảm bảo có view cho Part 2, Part 3, Part 4
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

if "def admin_part2_questions(request):" not in s:
    s += r'''

# ===== Listening Part 2 interface =====
def admin_part2_questions(request):
    return render(request, "core/listening_part2.html")
# ===== End Listening Part 2 interface =====
'''

if "def admin_part3_questions(request):" not in s:
    s += r'''

# ===== Listening Part 3 placeholder =====
def admin_part3_questions(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Part 3 đã được mở khung giao diện. Hiện chưa có dữ liệu, sẽ thiết kế chi tiết sau.",
    })
# ===== End Listening Part 3 placeholder =====
'''

if "def admin_part4_questions(request):" not in s:
    s += r'''

# ===== Listening Part 4 placeholder =====
def admin_part4_questions(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Part 4 đã được mở khung giao diện. Hiện chưa có dữ liệu, sẽ thiết kế chi tiết sau.",
    })
# ===== End Listening Part 4 placeholder =====
'''

views.write_text(s, encoding="utf-8")


# ==================================================
# 2) Đảm bảo core/urls.py có route cho đủ 4 Part
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if "from . import views" not in u:
    u = u.replace("from django.urls import path", "from django.urls import path\nfrom . import views", 1)

routes = {
    'dashboard/part-4/': '    path("dashboard/part-4/", views.admin_part2_questions, name="admin_part2_questions"),',
    'dashboard/part-3/': '    path("dashboard/part-3/", views.admin_part3_questions, name="admin_part3_questions"),',
    'dashboard/part-4/': '    path("dashboard/part-4/", views.admin_part4_questions, name="admin_part4_questions"),',
}

for key, route in routes.items():
    if key not in u:
        u = re.sub(
            r"urlpatterns\s*=\s*\[",
            "urlpatterns = [\n" + route,
            u,
            count=1
        )

# Sửa format nếu path Part 1 và listening bị dính cùng dòng
u = u.replace('name="admin_part1_questions"),    path("listening/"', 'name="admin_part1_questions"),\n    path("listening/"')

urls.write_text(u, encoding="utf-8")


# ==================================================
# 3) Tạo template placeholder cho Part 3/4
# ==================================================
placeholder = Path("templates/core/listening_part_placeholder.html")
placeholder.parent.mkdir(parents=True, exist_ok=True)

placeholder.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ part_title }} | Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">

    <style>
        :root {
            --red: #e60023;
            --red2: #ff5f76;
            --deep: #7a0010;
            --dark: #3f0011;
            --soft: #fff1f4;
            --line: #ffd1dc;
            --muted: #667085;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top right, rgba(255, 95, 118, .18), transparent 34%),
                linear-gradient(135deg, #fffafa 0%, #fff0f4 48%, #fff7f9 100%);
            color: var(--dark);
            font-family: "Segoe UI", Tahoma, Arial, sans-serif;
        }

        .wrap {
            max-width: 1180px;
            margin: 0 auto;
            padding: 34px 22px;
        }

        .topbar {
            border-left: 4px solid var(--red);
            background: linear-gradient(90deg, #fff1f4, #fff7f9);
            border-radius: 0 14px 14px 0;
            padding: 15px 19px;
            font-weight: 900;
            color: var(--deep);
            box-shadow: 0 10px 24px rgba(180, 0, 30, .06);
        }

        .hero {
            margin-top: 18px;
            background: rgba(255,255,255,.92);
            border: 1px solid var(--line);
            border-radius: 30px;
            padding: 34px;
            box-shadow: 0 20px 46px rgba(180,0,30,.08);
        }

        .badge {
            width: 72px;
            height: 72px;
            border-radius: 22px;
            display: grid;
            place-items: center;
            color: white;
            font-size: 34px;
            font-weight: 950;
            background: linear-gradient(135deg, var(--red), var(--red2));
            box-shadow: 0 18px 34px rgba(230, 0, 35, .18);
            margin-bottom: 20px;
        }

        h1 {
            margin: 0;
            font-size: clamp(38px, 5vw, 64px);
            line-height: 1;
            letter-spacing: -.05em;
            color: var(--dark);
            font-weight: 950;
        }

        p {
            margin: 18px 0 0;
            max-width: 760px;
            color: var(--muted);
            font-size: 20px;
            line-height: 1.7;
            font-weight: 650;
        }

        .empty-card {
            margin-top: 26px;
            border: 1px dashed #ff9cac;
            border-radius: 24px;
            padding: 28px;
            background: #fffafa;
            color: #8a0015;
            font-size: 18px;
            line-height: 1.6;
            font-weight: 750;
        }

        .actions {
            margin-top: 26px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .btn {
            min-height: 50px;
            padding: 0 22px;
            border: 0;
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-weight: 950;
            font-size: 16px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--red), var(--red2));
            color: white;
            box-shadow: 0 14px 28px rgba(230,0,35,.18);
        }

        .btn-light {
            background: #fff1f4;
            color: #8a0015;
            border: 1px solid var(--line);
        }
    </style>
</head>

<body>
    <main class="wrap">
        <section class="topbar">{{ part_title }}</section>

        <section class="hero">
            <div class="badge">{{ part_number }}</div>
            <h1>{{ part_title }}</h1>
            <p>{{ part_desc }}</p>

            <div class="empty-card">
                Dữ liệu của {{ part_title }} hiện chưa được nhập. Khi bạn bắt đầu làm phần này, mình sẽ tạo giao diện quản lý chi tiết giống Part 1/Part 2 nhưng không ảnh hưởng dữ liệu Part 1.
            </div>

            <div class="actions">
                <a class="btn btn-primary" href="/dashboard/listening-parts/">Quay lại chọn Part</a>
                <a class="btn btn-light" href="/dashboard/">Về Dashboard</a>
            </div>
        </section>
    </main>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 4) Đảm bảo template Part 2 tồn tại, nếu chưa có thì tạo khung đơn giản
# ==================================================
part2 = Path("templates/core/listening_part2.html")
if not part2.exists():
    part2.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Part 2 | Aptis</title>
    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
    <style>
        body {
            margin: 0;
            min-height: 100vh;
            padding: 28px;
            background: linear-gradient(135deg,#fffafa,#fff1f4);
            color: #3f0011;
            font-family: "Segoe UI", Tahoma, Arial, sans-serif;
        }
        .card {
            max-width: 1100px;
            margin: 0 auto;
            background: white;
            border: 1px solid #ffd1dc;
            border-radius: 28px;
            padding: 30px;
            box-shadow: 0 20px 46px rgba(180,0,30,.08);
        }
        h1 {
            margin: 0;
            font-size: 54px;
            letter-spacing: -.05em;
        }
        .topic {
            margin-top: 20px;
            padding: 16px 20px;
            border-radius: 999px;
            background: #fff1f4;
            color: #7a0010;
            font-weight: 900;
        }
        .empty {
            margin-top: 20px;
            padding: 24px;
            border: 1px dashed #ff9cac;
            border-radius: 20px;
            color: #667085;
            font-size: 18px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <section class="card">
        <h1>Part 2</h1>
        <div class="topic">Topic lớn + 4 voice thảo luận + pool đáp án A-B-C-D</div>
        <div class="empty">Khung Part 2 đã mở. Dữ liệu thật sẽ được nhập sau.</div>
    </section>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 5) Ghi lại trang Chọn Part thành bản mở đủ 4 Part
# ==================================================
parts_page = Path("templates/core/listening_parts.html")
parts_page.parent.mkdir(parents=True, exist_ok=True)

parts_page.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Chọn Part cần quản lý | Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">

    <style>
        :root {
            --red: #e60023;
            --red2: #ff5f76;
            --deep: #7a0010;
            --dark: #3f0011;
            --soft: #fff1f4;
            --line: #ffd1dc;
            --muted: #667085;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top right, rgba(255, 95, 118, .18), transparent 34%),
                linear-gradient(135deg, #fffafa 0%, #fff0f4 48%, #fff7f9 100%);
            color: var(--dark);
            font-family: "Segoe UI", Tahoma, Arial, sans-serif;
        }

        .wrap {
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 20px 40px;
        }

        .title-box {
            margin-bottom: 24px;
        }

        h1 {
            margin: 0;
            color: var(--dark);
            font-size: 30px;
            line-height: 1.2;
            font-weight: 950;
            letter-spacing: -.03em;
        }

        .subtitle {
            margin-top: 8px;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.6;
            font-weight: 650;
        }

        .part-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(250px, 1fr));
            gap: 18px;
        }

        .part-card {
            min-height: 300px;
            border: 1px solid var(--line);
            border-radius: 28px;
            background: rgba(255,255,255,.90);
            box-shadow: 0 20px 46px rgba(180,0,30,.07);
            padding: 24px;
            display: flex;
            flex-direction: column;
            transition: .18s ease;
        }

        .part-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 24px 54px rgba(180,0,30,.11);
        }

        .part-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
        }

        .part-number {
            width: 58px;
            height: 58px;
            border-radius: 18px;
            display: grid;
            place-items: center;
            color: white;
            background: linear-gradient(135deg, var(--red), var(--red2));
            font-size: 24px;
            font-weight: 950;
            box-shadow: 0 18px 34px rgba(230,0,35,.18);
        }

        .count-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 32px;
            padding: 0 14px;
            border-radius: 999px;
            border: 1px solid #ffb6c2;
            background: #fff1f4;
            color: #b8001c;
            font-weight: 950;
            font-size: 14px;
            white-space: nowrap;
        }

        .part-title {
            margin: 26px 0 12px;
            font-size: 38px;
            line-height: 1;
            color: var(--dark);
            font-weight: 950;
            letter-spacing: -.045em;
        }

        .part-desc {
            color: var(--muted);
            font-size: 16px;
            line-height: 1.7;
            font-weight: 650;
        }

        .part-actions {
            margin-top: auto;
            padding-top: 28px;
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
        }

        .status-pill {
            min-height: 42px;
            padding: 0 16px;
            border-radius: 999px;
            border: 1px solid #ffd1dc;
            background: #fffafa;
            color: #b8001c;
            display: inline-flex;
            align-items: center;
            font-weight: 950;
            font-size: 14px;
        }

        .open-btn {
            min-height: 48px;
            padding: 0 20px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            background: linear-gradient(135deg, var(--red), var(--red2));
            text-decoration: none;
            font-weight: 950;
            box-shadow: 0 16px 30px rgba(230,0,35,.16);
            white-space: nowrap;
        }

        .open-btn.secondary {
            background: #fff1f4;
            color: #b8001c;
            border: 1px solid #ffb6c2;
            box-shadow: none;
        }

        @media (max-width: 1180px) {
            .part-grid {
                grid-template-columns: repeat(2, minmax(250px, 1fr));
            }
        }

        @media (max-width: 640px) {
            .part-grid {
                grid-template-columns: 1fr;
            }

            .part-card {
                min-height: auto;
            }
        }
    </style>
</head>

<body>
    <main class="wrap">
        <section class="title-box">
            <h1>Chọn Part cần quản lý</h1>
            <div class="subtitle">
                Hiển thị 4 part theo dạng thẻ bo tròn. Part nào chưa có dữ liệu thì vẫn mở khung để chuẩn bị nhập sau.
            </div>
        </section>

        <section class="part-grid">
            <article class="part-card">
                <div class="part-top">
                    <div class="part-number">1</div>
                    <div class="count-pill">191 câu hỏi</div>
                </div>

                <h2 class="part-title">Part 1</h2>
                <div class="part-desc">
                    Cập nhật hàng loạt câu hỏi, audio, đáp án và transcript cho Part 1. Đây là phần đã chốt giao diện/logic.
                </div>

                <div class="part-actions">
                    <span class="status-pill">Đã chốt giao diện</span>
                    <a class="open-btn" href="/dashboard/part-4/">Mở Part 4</a>
                </div>
            </article>

            <article class="part-card">
                <div class="part-top">
                    <div class="part-number">2</div>
                    <div class="count-pill">0 câu hỏi</div>
                </div>

                <h2 class="part-title">Part 2</h2>
                <div class="part-desc">
                    Part 2 gồm 1 chủ đề lớn, 4 voice thảo luận và pool đáp án A-B-C-D. Hiện đã mở khung giao diện.
                </div>

                <div class="part-actions">
                    <span class="status-pill">Đã mở khung</span>
                    <a class="open-btn" href="/dashboard/part-4/">Mở Part 4</a>
                </div>
            </article>

            <article class="part-card">
                <div class="part-top">
                    <div class="part-number">3</div>
                    <div class="count-pill">0 câu hỏi</div>
                </div>

                <h2 class="part-title">Part 3</h2>
                <div class="part-desc">
                    Part 3 hiện chưa có dữ liệu. Đã mở trang khung để sau này thiết kế và nhập nội dung.
                </div>

                <div class="part-actions">
                    <span class="status-pill">Chưa có dữ liệu</span>
                    <a class="open-btn secondary" href="/dashboard/part-4/">Mở Part 4</a>
                </div>
            </article>

            <article class="part-card">
                <div class="part-top">
                    <div class="part-number">4</div>
                    <div class="count-pill">0 câu hỏi</div>
                </div>

                <h2 class="part-title">Part 4</h2>
                <div class="part-desc">
                    Part 4 hiện chưa có dữ liệu. Đã mở trang khung để sau này thiết kế và nhập nội dung.
                </div>

                <div class="part-actions">
                    <span class="status-pill">Chưa có dữ liệu</span>
                    <a class="open-btn secondary" href="/dashboard/part-4/">Mở Part 4</a>
                </div>
            </article>
        </section>
    </main>
</body>
</html>
''', encoding="utf-8")

print("DA_MO_DAY_DU_4_PART_PART_NAO_CHUA_LAM_THI_CHUA_CO_DU_LIEU")
