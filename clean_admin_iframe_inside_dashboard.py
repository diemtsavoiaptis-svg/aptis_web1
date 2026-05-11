from pathlib import Path
import re

p = Path("templates/core/dashboard.html")
s = p.read_text(encoding="utf-8", errors="ignore")

# Backup
Path("templates/core/dashboard.html.bak_clean_iframe_admin").write_text(s, encoding="utf-8")

# 1) Add CSS cho iframe rộng và sạch hơn
css = r'''
/* Làm khung bên phải rộng, sạch, không có admin mini sidebar */
#adminFrame {
    width: 100% !important;
    height: calc(100vh - 245px) !important;
    min-height: 720px !important;
    border: 0 !important;
    background: #fffafa !important;
}

.content-card {
    min-height: calc(100vh - 185px) !important;
}

.frame-toolbar {
    display: none !important;
}
'''

if "không có admin mini sidebar" not in s:
    s = s.replace("</style>", css + "\n</style>", 1)

# 2) Add JS tự chui vào iframe để ẩn sidebar/header của Django Admin
inject_js = r'''
function cleanAdminIframe(){
    const frame = document.getElementById("adminFrame");
    if(!frame || frame.hidden) return;

    try {
        const doc = frame.contentDocument || frame.contentWindow.document;
        if(!doc) return;

        if(doc.getElementById("clean-admin-iframe-style")) return;

        const style = doc.createElement("style");
        style.id = "clean-admin-iframe-style";
        style.textContent = `
            /* Ẩn toàn bộ phần admin phụ bên trong iframe */
            #header,
            div.breadcrumbs,
            #nav-sidebar,
            .toggle-nav-sidebar,
            #changelist-filter,
            .object-tools,
            .paginator,
            .actions label,
            .actions select,
            .actions button,
            .actions span,
            #toolbar,
            #changelist-search img {
                display: none !important;
            }

            html, body {
                margin: 0 !important;
                padding: 0 !important;
                background: #fffafa !important;
                overflow-x: hidden !important;
                font-family: Georgia, "Times New Roman", serif !important;
            }

            #container,
            #main,
            .main,
            #content,
            .content,
            .content-main,
            #changelist,
            #changelist-form,
            .results {
                width: 100% !important;
                max-width: none !important;
                margin: 0 !important;
                padding: 0 !important;
                left: 0 !important;
                float: none !important;
                box-sizing: border-box !important;
            }

            #content {
                padding: 22px 24px !important;
            }

            #content h1 {
                font-size: 34px !important;
                line-height: 1.15 !important;
                margin: 0 0 22px !important;
                color: #3f0011 !important;
                font-weight: 950 !important;
                letter-spacing: -0.04em !important;
            }

            /* Thanh tìm kiếm đẹp hơn */
            #changelist-search {
                display: flex !important;
                align-items: center !important;
                gap: 10px !important;
                margin: 0 0 18px !important;
                padding: 14px !important;
                background: #fff1f4 !important;
                border: 1px solid #ffd1dc !important;
                border-radius: 18px !important;
            }

            #changelist-search input[type="text"] {
                flex: 1 !important;
                height: 44px !important;
                border-radius: 14px !important;
                border: 1px solid #ffd1dc !important;
                padding: 0 16px !important;
                font-size: 16px !important;
            }

            #changelist-search input[type="submit"] {
                height: 44px !important;
                border-radius: 14px !important;
                border: 0 !important;
                background: linear-gradient(135deg, #e60023, #ff5f76) !important;
                color: white !important;
                font-weight: 900 !important;
                padding: 0 22px !important;
            }

            /* Bảng rộng, dễ thao tác */
            table {
                width: 100% !important;
                border-collapse: separate !important;
                border-spacing: 0 !important;
                background: white !important;
                border: 1px solid #ffd1dc !important;
                border-radius: 20px !important;
                overflow: hidden !important;
                font-size: 15px !important;
            }

            thead th {
                background: #fff1f4 !important;
                color: #7a0010 !important;
                font-weight: 950 !important;
                padding: 12px !important;
                white-space: nowrap !important;
            }

            tbody td,
            tbody th {
                padding: 12px !important;
                border-bottom: 1px solid #ffe1e7 !important;
                vertical-align: middle !important;
            }

            tbody tr:hover {
                background: #fff8fa !important;
            }

            a {
                color: #8a0015 !important;
                font-weight: 850 !important;
            }

            input, select, textarea {
                border-radius: 12px !important;
                border: 1px solid #ffd1dc !important;
            }

            .button,
            input[type="submit"],
            input[type="button"],
            a.button {
                border-radius: 12px !important;
                background: #e60023 !important;
                color: white !important;
                border: 0 !important;
                font-weight: 900 !important;
            }
        `;

        doc.head.appendChild(style);

        // Đổi một số chữ cho gọn
        const h1 = doc.querySelector("#content h1");
        if(h1 && h1.textContent.includes("Chọn Student")) {
            h1.textContent = "Duyệt student";
        }

    } catch(e) {
        console.log("Không thể làm sạch iframe admin:", e);
    }
}
'''

if "function cleanAdminIframe()" not in s:
    s = s.replace("function reloadFrame(){", inject_js + "\nfunction reloadFrame(){", 1)

# 3) Gắn sự kiện iframe load
if 'frame.addEventListener("load", cleanAdminIframe);' not in s:
    s = s.replace(
        'frame.hidden = false;',
        'frame.hidden = false;\n    frame.addEventListener("load", cleanAdminIframe);',
        1
    )

# 4) Sau khi set src thì gọi clean sau chút
if "setTimeout(cleanAdminIframe, 300);" not in s:
    s = s.replace(
        "frame.src = url;",
        "frame.src = url;\n        setTimeout(cleanAdminIframe, 300);",
        1
    )

p.write_text(s, encoding="utf-8")
print("DA_AN_ADMIN_SIDEBAR_BE_BE_TRONG_IFRAME")
