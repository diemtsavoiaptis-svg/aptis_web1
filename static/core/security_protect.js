
(function () {
    const EVENT_URL = "/security/event/";
    const PRINT_LIMIT = 3;
    const PRINT_WINDOW_MS = 60000;

    let printScreenTimes = [];
    let devtoolsWarned = false;

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }

    function sendSecurityEvent(reason) {
        try {
            fetch(EVENT_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                credentials: "same-origin",
                body: JSON.stringify({ reason: reason })
            }).catch(() => {});
        } catch (e) {}
    }

    // Không cảnh báo khi student rời tab/quay lại tab nữa.
    // visibilitychange / blur / focus được bỏ để tránh báo sai.

    // Cảnh báo nếu student bấm PrintScreen nhiều lần.
    document.addEventListener("keyup", function (e) {
        if (e.key !== "PrintScreen") return;

        const now = Date.now();
        printScreenTimes = printScreenTimes.filter(t => now - t < PRINT_WINDOW_MS);
        printScreenTimes.push(now);

        if (printScreenTimes.length >= PRINT_LIMIT) {
            sendSecurityEvent("Student có dấu hiệu chụp màn hình liên tục");
            printScreenTimes = [];
        }
    });

    // Cảnh báo mở DevTools/công cụ kiểm tra trang.
    setInterval(function () {
        const widthGap = window.outerWidth - window.innerWidth;
        const heightGap = window.outerHeight - window.innerHeight;

        if (!devtoolsWarned && (widthGap > 180 || heightGap > 180)) {
            devtoolsWarned = true;
            sendSecurityEvent("Student có dấu hiệu mở công cụ kiểm tra trang");
        }

        if (widthGap <= 120 && heightGap <= 120) {
            devtoolsWarned = false;
        }
    }, 1500);
})();
