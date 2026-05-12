
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
