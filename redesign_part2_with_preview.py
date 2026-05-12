from pathlib import Path
import shutil
from datetime import datetime

print("=== REDESIGN PART 2 ONLY WITH PREVIEW ===")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_part2_redesign_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

# Backup templates/static only
for folder in ["templates", "static"]:
    p = Path(folder)
    if p.exists():
        shutil.copytree(p, backup_dir / folder, dirs_exist_ok=True)

css_dir = Path("static/css")
js_dir = Path("static/js")
css_dir.mkdir(parents=True, exist_ok=True)
js_dir.mkdir(parents=True, exist_ok=True)

css_file = css_dir / "part2_design_system.css"
js_file = js_dir / "part2_design_system.js"

css_file.write_text(r'''
/* =========================================================
   PART 2 DESIGN SYSTEM ONLY
   Brand: TSA Primary #b21c24 / Coral #e63946
   ========================================================= */

:root {
    --tsa-primary: #b21c24;
    --tsa-coral: #e63946;
    --tsa-soft: #fef2f2;
    --tsa-slate: #f8fafc;
    --tsa-ink: #101827;
    --tsa-muted: #64748b;
    --tsa-border: rgba(178, 28, 36, 0.16);
    --tsa-radius-xl: 2rem;
    --tsa-radius-2xl: 2.5rem;
    --tsa-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
    --tsa-red-shadow: 0 18px 38px rgba(178, 28, 36, 0.28);
    --tsa-font: "Inter", "Lexend", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body.tsa-part2-student,
body.tsa-part2-admin {
    font-family: var(--tsa-font) !important;
    background: var(--tsa-slate) !important;
    color: var(--tsa-ink) !important;
}

/* =========================
   STUDENT PART 2
   ========================= */

body.tsa-part2-student .student-part2-shell,
body.tsa-part2-student .part2-student-shell,
body.tsa-part2-student main,
body.tsa-part2-student .main-content,
body.tsa-part2-student .content {
    max-width: 1280px !important;
    margin: 0 auto !important;
    padding: 28px !important;
    box-sizing: border-box !important;
}

body.tsa-part2-student .tsa-part2-student-grid {
    display: grid !important;
    grid-template-columns: minmax(0, 3fr) minmax(260px, 1fr) !important;
    gap: 28px !important;
    align-items: start !important;
}

body.tsa-part2-student .tsa-part2-main-card,
body.tsa-part2-student .tsa-part2-side-card,
body.tsa-part2-student .card,
body.tsa-part2-student .panel,
body.tsa-part2-student section {
    border-radius: var(--tsa-radius-2xl) !important;
    border: 1px solid var(--tsa-border) !important;
    background: #fff !important;
    box-shadow: var(--tsa-shadow) !important;
}

body.tsa-part2-student .tsa-part2-guide {
    background: var(--tsa-soft) !important;
    border-left: 7px solid var(--tsa-primary) !important;
    border-radius: 1.5rem !important;
    padding: 18px 22px !important;
    margin-bottom: 22px !important;
    font-weight: 800 !important;
    color: var(--tsa-primary) !important;
}

body.tsa-part2-student h1,
body.tsa-part2-student h2,
body.tsa-part2-student .topic-title,
body.tsa-part2-student [class*="title"] {
    color: var(--tsa-ink) !important;
    font-weight: 950 !important;
    letter-spacing: -0.04em !important;
}

body.tsa-part2-student audio {
    width: 100% !important;
    accent-color: var(--tsa-primary) !important;
    border-radius: 999px !important;
}

body.tsa-part2-student .audio-box,
body.tsa-part2-student .audio-player,
body.tsa-part2-student [class*="audio"] {
    border-radius: 1.7rem !important;
}

body.tsa-part2-student select,
body.tsa-part2-student .select,
body.tsa-part2-student input,
body.tsa-part2-student textarea {
    min-height: 58px !important;
    border-radius: 1.4rem !important;
    border: 1.5px solid rgba(178, 28, 36, 0.18) !important;
    background: #f8fafc !important;
    font-weight: 850 !important;
    color: #334155 !important;
    padding: 0 18px !important;
    outline: none !important;
}

body.tsa-part2-student select:focus,
body.tsa-part2-student input:focus,
body.tsa-part2-student textarea:focus {
    border-color: var(--tsa-primary) !important;
    box-shadow: 0 0 0 5px rgba(178, 28, 36, 0.10) !important;
    background: #fff !important;
}

body.tsa-part2-student label,
body.tsa-part2-student .speaker-label,
body.tsa-part2-student [class*="speaker"] {
    font-weight: 950 !important;
}

body.tsa-part2-student .speaker-label,
body.tsa-part2-student [class*="kicker"] {
    text-transform: uppercase !important;
    letter-spacing: 0.28em !important;
    font-size: 11px !important;
    font-style: italic !important;
    color: #94a3b8 !important;
}

body.tsa-part2-student button,
body.tsa-part2-student .btn,
body.tsa-part2-student a[class*="btn"] {
    border-radius: 1.2rem !important;
    font-weight: 950 !important;
}

body.tsa-part2-student .primary-btn,
body.tsa-part2-student button[type="submit"],
body.tsa-part2-student .save-btn,
body.tsa-part2-student .btn-primary {
    background: var(--tsa-primary) !important;
    color: #fff !important;
    box-shadow: var(--tsa-red-shadow) !important;
    border: 0 !important;
}

body.tsa-part2-student .tsa-part2-progress {
    height: 5px !important;
    background: rgba(178, 28, 36, 0.12) !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    margin-bottom: 22px !important;
}

body.tsa-part2-student .tsa-part2-progress > span {
    display: block !important;
    width: var(--progress, 25%) !important;
    height: 100% !important;
    background: var(--tsa-coral) !important;
    border-radius: 999px !important;
}

/* =========================
   ADMIN PART 2
   ========================= */

body.tsa-part2-admin {
    background: #f8fafc !important;
}

body.tsa-part2-admin .sidebar,
body.tsa-part2-admin .admin-sidebar,
body.tsa-part2-admin .dashboard-sidebar,
body.tsa-part2-admin aside {
    width: 240px !important;
    min-width: 240px !important;
    background: var(--tsa-primary) !important;
}

body.tsa-part2-admin main,
body.tsa-part2-admin .main-content,
body.tsa-part2-admin .dashboard-main,
body.tsa-part2-admin .content,
body.tsa-part2-admin .admin-main {
    margin-left: 240px !important;
    width: calc(100vw - 240px) !important;
    max-width: calc(100vw - 240px) !important;
    padding: 30px !important;
    box-sizing: border-box !important;
}

body.tsa-part2-admin h1 {
    font-size: clamp(38px, 4vw, 64px) !important;
    font-weight: 1000 !important;
    letter-spacing: -0.06em !important;
    color: var(--tsa-ink) !important;
}

body.tsa-part2-admin h2,
body.tsa-part2-admin h3 {
    font-weight: 950 !important;
    color: var(--tsa-ink) !important;
}

body.tsa-part2-admin .card,
body.tsa-part2-admin .panel,
body.tsa-part2-admin section,
body.tsa-part2-admin .admin-card {
    border-radius: var(--tsa-radius-2xl) !important;
    border: 1px solid rgba(15, 23, 42, 0.07) !important;
    background: #fff !important;
    box-shadow: var(--tsa-shadow) !important;
}

body.tsa-part2-admin input,
body.tsa-part2-admin textarea,
body.tsa-part2-admin select {
    min-height: 56px !important;
    border-radius: 1.2rem !important;
    border: 1px solid rgba(148, 163, 184, 0.32) !important;
    background: #f8fafc !important;
    font-weight: 800 !important;
    outline: none !important;
}

body.tsa-part2-admin input:focus,
body.tsa-part2-admin textarea:focus,
body.tsa-part2-admin select:focus {
    border-color: var(--tsa-primary) !important;
    box-shadow: 0 0 0 5px rgba(178, 28, 36, 0.10) !important;
    background: #fff !important;
}

body.tsa-part2-admin button,
body.tsa-part2-admin .btn,
body.tsa-part2-admin a[class*="btn"] {
    min-height: 50px !important;
    border-radius: 1rem !important;
    font-weight: 950 !important;
}

body.tsa-part2-admin button[type="submit"],
body.tsa-part2-admin .btn-primary,
body.tsa-part2-admin .save-btn,
body.tsa-part2-admin .tsa-save-data-btn {
    background: var(--tsa-primary) !important;
    color: #fff !important;
    border: 0 !important;
    box-shadow: var(--tsa-red-shadow) !important;
}

.tsa-preview-open-btn {
    border: 1px solid rgba(148, 163, 184, 0.38) !important;
    background: #fff !important;
    color: #475569 !important;
    padding: 0 22px !important;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08) !important;
}

.tsa-preview-modal {
    position: fixed;
    inset: 0;
    z-index: 2147483600;
    background: rgba(15, 23, 42, 0.72);
    backdrop-filter: blur(8px);
    display: none;
    align-items: center;
    justify-content: center;
    padding: 28px;
}

.tsa-preview-modal.is-open {
    display: flex;
}

.tsa-preview-modal-card {
    width: min(1180px, 96vw);
    max-height: 92vh;
    overflow: auto;
    background: #f8fafc;
    border-radius: 2rem;
    box-shadow: 0 30px 100px rgba(0,0,0,0.32);
    padding: 26px;
}

.tsa-preview-modal-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}

.tsa-preview-modal-head h2 {
    margin: 0;
    font-weight: 1000;
    letter-spacing: -0.04em;
}

.tsa-preview-close {
    border: 0;
    background: var(--tsa-primary);
    color: #fff;
    width: 46px;
    height: 46px;
    border-radius: 999px;
    font-weight: 1000;
    cursor: pointer;
}

.tsa-preview-student {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(250px, 1fr);
    gap: 24px;
}

.tsa-preview-left,
.tsa-preview-right {
    border-radius: 2rem;
    background: #fff;
    border: 1px solid var(--tsa-border);
    box-shadow: var(--tsa-shadow);
    padding: 26px;
}

.tsa-preview-guide {
    background: var(--tsa-soft);
    border-left: 7px solid var(--tsa-primary);
    border-radius: 1.3rem;
    padding: 16px 18px;
    margin-bottom: 18px;
    font-weight: 850;
    color: var(--tsa-primary);
}

.tsa-preview-audio {
    border-radius: 1.5rem;
    background: #fff7f7;
    border: 1px solid rgba(230, 57, 70, 0.18);
    padding: 20px;
    margin: 18px 0;
}

.tsa-preview-speaker {
    margin: 18px 0;
}

.tsa-preview-speaker small {
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.28em;
    font-style: italic;
    color: #94a3b8;
    font-weight: 950;
    margin-bottom: 8px;
}

.tsa-preview-speaker select {
    width: 100%;
    min-height: 58px;
    border-radius: 1.35rem;
    border: 1.5px solid rgba(178,28,36,0.18);
    background: #f8fafc;
    padding: 0 18px;
    font-weight: 900;
}

.tsa-preview-save {
    width: 100%;
    min-height: 56px;
    border: 0;
    border-radius: 1.2rem;
    background: var(--tsa-primary);
    color: #fff;
    font-weight: 1000;
    box-shadow: var(--tsa-red-shadow);
}

.tsa-preview-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}

.tsa-preview-stat {
    border-radius: 1.4rem;
    background: #f8fafc;
    padding: 18px;
    text-align: center;
}

.tsa-preview-stat strong {
    display: block;
    font-size: 30px;
    color: var(--tsa-primary);
    font-weight: 1000;
}

@media (max-width: 900px) {
    .tsa-preview-student,
    body.tsa-part2-student .tsa-part2-student-grid {
        grid-template-columns: 1fr !important;
    }

    body.tsa-part2-admin main,
    body.tsa-part2-admin .main-content,
    body.tsa-part2-admin .dashboard-main,
    body.tsa-part2-admin .content,
    body.tsa-part2-admin .admin-main {
        margin-left: 0 !important;
        width: 100vw !important;
        max-width: 100vw !important;
    }
}
''', encoding="utf-8")

js_file.write_text(r'''
(function () {
    function isPart2Page() {
        const path = window.location.pathname.toLowerCase();
        const text = document.body.innerText || "";
        return path.includes("part-2") || path.includes("part2") || text.includes("Part 2") || text.includes("Thiết lập Part 2");
    }

    function isAdminPage() {
        const path = window.location.pathname.toLowerCase();
        const text = document.body.innerText || "";
        return path.includes("dashboard") || text.includes("Thiết lập Part 2") || text.includes("LƯU DỮ LIỆU");
    }

    function secureStudentAudio() {
        document.querySelectorAll("audio").forEach(function (audio) {
            audio.setAttribute("controlsList", "nodownload noplaybackrate");
            audio.setAttribute("disablePictureInPicture", "true");
        });
    }

    function addSecurity() {
        document.addEventListener("contextmenu", function (e) {
            e.preventDefault();
        });

        document.addEventListener("keydown", function (e) {
            const key = (e.key || "").toLowerCase();
            if (
                e.key === "F12" ||
                (e.ctrlKey && e.shiftKey && ["i", "j", "c"].includes(key)) ||
                (e.ctrlKey && ["u", "s"].includes(key))
            ) {
                e.preventDefault();
                return false;
            }
        });
    }

    function readAdminData() {
        const get = (sel) => {
            const el = document.querySelector(sel);
            return el ? (el.value || el.innerText || "").trim() : "";
        };

        let topic =
            get('input[name*="topic"]') ||
            get('input[placeholder*="Topic"]') ||
            get('input[placeholder*="topic"]') ||
            "Chưa đặt Topic";

        const options = Array.from(document.querySelectorAll("option, .option-item, li"))
            .map(el => (el.innerText || el.textContent || "").trim())
            .filter(t => t && t.length < 80)
            .slice(0, 8);

        const safeOptions = options.length ? options : ["In various places", "In a quiet place", "At home", "In a library"];

        return { topic, options: safeOptions };
    }

    function createPreviewModal() {
        if (document.getElementById("tsaPreviewModal")) return;

        const data = readAdminData();
        const optionHtml = data.options.map(o => `<option>${o}</option>`).join("");

        const modal = document.createElement("div");
        modal.id = "tsaPreviewModal";
        modal.className = "tsa-preview-modal";
        modal.innerHTML = `
            <div class="tsa-preview-modal-card">
                <div class="tsa-preview-modal-head">
                    <h2>Preview giao diện học viên Part 2</h2>
                    <button class="tsa-preview-close" type="button">×</button>
                </div>
                <div class="tsa-preview-student">
                    <div class="tsa-preview-left">
                        <div class="tsa-preview-guide">
                            Part 2: Nghe audio tổng và chọn đáp án phù hợp cho 4 Speaker.
                        </div>
                        <h1>Topic: ${data.topic || "Chưa đặt Topic"}</h1>
                        <div class="tsa-preview-audio">
                            <audio controls controlsList="nodownload noplaybackrate"></audio>
                        </div>
                        ${[1,2,3,4].map(i => `
                            <div class="tsa-preview-speaker">
                                <small>Speaker ${i}</small>
                                <select>
                                    <option>Chọn đáp án...</option>
                                    ${optionHtml}
                                </select>
                            </div>
                        `).join("")}
                        <div style="display:flex;gap:12px;margin-top:22px;flex-wrap:wrap;">
                            <button type="button" class="tsa-preview-open-btn">Previous</button>
                            <button type="button" class="tsa-preview-open-btn">Next</button>
                            <button type="button" class="tsa-preview-save" style="max-width:220px;">LƯU LẠI</button>
                        </div>
                    </div>
                    <div class="tsa-preview-right">
                        <div class="tsa-preview-stats">
                            <div class="tsa-preview-stat"><strong>0</strong><span>Đã thuộc</span></div>
                            <div class="tsa-preview-stat"><strong>0</strong><span>Đánh dấu</span></div>
                        </div>
                        <button type="button" class="tsa-preview-save">LƯU LẠI 💾</button>
                        <p style="text-align:center;color:#64748b;font-weight:800;margin-top:12px;">Kiểm tra kỹ trước khi lưu</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector(".tsa-preview-close").addEventListener("click", function () {
            modal.classList.remove("is-open");
        });

        modal.addEventListener("click", function (e) {
            if (e.target === modal) modal.classList.remove("is-open");
        });
    }

    function ensurePreviewButton() {
        if (document.getElementById("tsaPreviewOpenBtn")) return;

        const header = document.querySelector("header, .header, .page-header, .admin-header, main, .main-content, .content");
        if (!header) return;

        const btn = document.createElement("button");
        btn.id = "tsaPreviewOpenBtn";
        btn.type = "button";
        btn.className = "tsa-preview-open-btn";
        btn.innerHTML = "👁️ PREVIEW";
        btn.style.position = "fixed";
        btn.style.top = "28px";
        btn.style.right = "190px";
        btn.style.zIndex = "9999";

        btn.addEventListener("click", function () {
            createPreviewModal();
            document.getElementById("tsaPreviewModal").classList.add("is-open");
        });

        document.body.appendChild(btn);
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (!isPart2Page()) return;

        if (isAdminPage()) {
            document.body.classList.add("tsa-part2-admin");
            ensurePreviewButton();

            document.querySelectorAll("button, a").forEach(function (el) {
                const text = (el.innerText || "").trim().toUpperCase();
                if (text.includes("PREVIEW")) {
                    el.addEventListener("click", function (e) {
                        e.preventDefault();
                        createPreviewModal();
                        document.getElementById("tsaPreviewModal").classList.add("is-open");
                    });
                }
            });
        } else {
            document.body.classList.add("tsa-part2-student");
        }

        secureStudentAudio();
        addSecurity();
    });
})();
''', encoding="utf-8")

# Inject only into Part 2 related templates
target_tokens = ["part2", "part_2", "part-2", "listening_part2", "student_part2", "admin_part2"]

updated = []
for path in Path("templates").rglob("*.html"):
    low = str(path).lower()
    content = path.read_text(encoding="utf-8", errors="ignore")
    should_update = any(t in low for t in target_tokens) or "Thiết lập Part 2" in content or "Manage Part 2" in content

    if not should_update:
        continue

    original = content

    if "{% load static %}" not in content:
        content = "{% load static %}\n" + content

    if "part2_design_system.css" not in content and "</head>" in content:
        content = content.replace(
            "</head>",
            '    <link rel="stylesheet" href="{% static \'css/part2_design_system.css\' %}">\n</head>'
        )

    if "part2_design_system.js" not in content and "</body>" in content:
        content = content.replace(
            "</body>",
            '    <script src="{% static \'js/part2_design_system.js\' %}"></script>\n</body>'
        )

    if content != original:
        shutil.copy2(path, backup_dir / str(path).replace("\\", "__").replace("/", "__"))
        path.write_text(content, encoding="utf-8")
        updated.append(str(path))

print("Updated Part 2 templates:")
for item in updated:
    print("-", item)

print("DONE")
print("Backup:", backup_dir)
print("CSS:", css_file)
print("JS:", js_file)
