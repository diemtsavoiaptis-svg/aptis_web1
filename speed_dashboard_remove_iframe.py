from pathlib import Path

tpl = Path("templates/core/dashboard.html")
html = tpl.read_text(encoding="utf-8-sig")

# Replace iframe-style menu buttons with direct navigation buttons.
html = html.replace(
    '''<button class="side-link" type="button"
                    data-title="Quản lý câu hỏi Listening"
                    data-desc="Chọn Part và cập nhật dữ liệu câu hỏi, audio, đáp án, transcript."
                    data-url="/dashboard/listening-parts/">
                🎧 Quản lý câu hỏi Listening
            </button>''',
    '''<button class="side-link" type="button" onclick="window.location.href='/dashboard/listening-parts/'">
                🎧 Quản lý câu hỏi Listening
            </button>'''
)

html = html.replace(
    '''<button class="side-link" type="button"
                    data-title="Duyệt học viên"
                    data-desc="Duyệt tài khoản học viên mới đăng ký, quản lý trạng thái học viên."
                    data-url="/dashboard/students/">
                ✅ Duyệt học viên
            </button>''',
    '''<button class="side-link" type="button" onclick="window.location.href='/dashboard/students/'">
                ✅ Duyệt học viên
            </button>'''
)

html = html.replace(
    '''<button class="side-link" type="button"
                    data-title="Quản lý bài học"
                    data-desc="Thêm, sửa và quản lý bài học hiển thị cho học viên."
                    data-url="/admin/core/lesson/">
                📚 Quản lý bài học
            </button>''',
    '''<button class="side-link" type="button" onclick="window.location.href='/admin/core/lesson/'">
                📚 Quản lý bài học
            </button>'''
)

html = html.replace(
    '''<button class="side-link" type="button"
                    data-title="Cảnh báo bảo mật"
                    data-desc="Theo dõi cảnh báo đăng nhập và các vấn đề bảo mật tài khoản."
                    data-url="/admin/core/securityalert/">
                🛡️ Cảnh báo bảo mật
            </button>''',
    '''<button class="side-link" type="button" onclick="window.location.href='/admin/core/securityalert/'">
                🛡️ Cảnh báo bảo mật
            </button>'''
)

html = html.replace(
    '''<button class="side-link" type="button"
                    data-title="Giao diện học viên"
                    data-desc="Xem nhanh giao diện luyện đề mà học viên đang sử dụng."
                    data-url="/listening/">
                👀 Xem giao diện học viên
            </button>''',
    '''<button class="side-link" type="button" onclick="window.location.href='/listening/'">
                👀 Xem giao diện học viên
            </button>'''
)

# Make quick cards direct links through JS-lite onclick.
html = html.replace(
    '<div class="quick-card" data-url="/dashboard/listening-parts/" data-title="Quản lý câu hỏi Listening" data-desc="Chọn Part và cập nhật dữ liệu câu hỏi, audio, đáp án, transcript.">',
    '<div class="quick-card" onclick="window.location.href=\'/dashboard/listening-parts/\'">'
)

html = html.replace(
    '<div class="quick-card" data-url="/dashboard/students/" data-title="Duyệt học viên" data-desc="Duyệt tài khoản học viên mới đăng ký, quản lý trạng thái học viên.">',
    '<div class="quick-card" onclick="window.location.href=\'/dashboard/students/\'">'
)

html = html.replace(
    '<div class="quick-card" data-url="/admin/core/lesson/" data-title="Quản lý bài học" data-desc="Thêm, sửa và quản lý bài học hiển thị cho học viên.">',
    '<div class="quick-card" onclick="window.location.href=\'/admin/core/lesson/\'">'
)

# Hide iframe content card on dashboard home to reduce layout work.
html = html.replace(
    '<section class="content-card">',
    '<section class="content-card fast-dashboard-card">'
)

extra_css = '''
<style id="fast-dashboard-no-iframe">
.fast-dashboard-card {
    min-height: auto !important;
}
#adminFrame,
.frame-toolbar {
    display: none !important;
}
</style>
'''

if 'id="fast-dashboard-no-iframe"' not in html:
    html = html.replace("</head>", extra_css + "\n</head>")

# Disable the heavy iframe JS by short-circuiting it.
html = html.replace(
    '<script>\nlet currentUrl = "";',
    '<script>\nlet currentUrl = "";\n/* Fast dashboard mode: iframe loading disabled. */'
)

html = html.replace(
    'function openFrame(url, title, desc){',
    'function openFrame(url, title, desc){ window.location.href = url; return;'
)

html = html.replace(
    'function openCurrentInNewTab(){\n    if(currentUrl){',
    'function openCurrentInNewTab(){\n    window.open("/admin/", "_blank"); return;\n    if(currentUrl){'
)

tpl.write_text(html, encoding="utf-8")
print("Done: Dashboard now opens pages directly instead of loading slow iframe.")
