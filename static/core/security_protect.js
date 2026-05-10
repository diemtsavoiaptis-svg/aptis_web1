(function () {
    "use strict";

    document.documentElement.classList.add("tsa-protected");

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }

    function reportSecurityEvent(eventType, severity) {
        try {
            fetch("/security/event/", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: new URLSearchParams({
                    event_type: eventType,
                    severity: severity || "medium"
                })
            });
        } catch (error) {}
    }

    function blockEvent(event, eventType, severity) {
        if (eventType) {
            reportSecurityEvent(eventType, severity || "medium");
        }
        event.preventDefault();
        event.stopPropagation();
        return false;
    }

    document.addEventListener("keydown", function (event) {
        const key = String(event.key || "").toLowerCase();

        if (event.key === "F12") {
            return blockEvent(event, "devtools_attempt", "high");
        }

        if (event.ctrlKey || event.metaKey) {
            if (key === "s") {
                return blockEvent(event, "save_attempt", "high");
            }
            if (key === "p") {
                return blockEvent(event, "print_attempt", "critical");
            }
            if (key === "u") {
                return blockEvent(event, "source_attempt", "high");
            }
        }

        if (event.ctrlKey && event.shiftKey) {
            if (["i", "j", "c"].includes(key)) {
                return blockEvent(event, "devtools_attempt", "high");
            }
        }

        if (event.key === "PrintScreen") {
            try {
                navigator.clipboard.writeText("Nội dung được bảo vệ bởi TSA Aptis.");
            } catch (error) {}
            return blockEvent(event, "screenshot_key", "high");
        }
    }, true);

    window.addEventListener("beforeprint", function (event) {
        return blockEvent(event, "print_attempt", "critical");
    });

    const focusShield = document.createElement("div");
    focusShield.className = "security-focus-shield";
    focusShield.innerHTML = `
        <div class="security-focus-shield-box">
            <h2>Nội dung đang được bảo vệ</h2>
            <p>Vui lòng quay lại cửa sổ học tập để tiếp tục làm bài. Nội dung đã được gắn watermark theo tài khoản đăng nhập.</p>
        </div>
    `;
    document.body.appendChild(focusShield);

    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            reportSecurityEvent("tab_blur", "low");
            focusShield.classList.add("show");
        } else {
            focusShield.classList.remove("show");
        }
    });

    setInterval(function () {
        const now = new Date();
        document.querySelectorAll("[data-security-time]").forEach(function (item) {
            item.textContent = now.toLocaleString("vi-VN");
        });
    }, 1000);
})();
