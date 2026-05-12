
(function () {
    function repeatText(text, count) {
        let out = "";
        for (let i = 0; i < count; i++) {
            out += text + "     ";
        }
        return out;
    }

    document.addEventListener("DOMContentLoaded", function () {
        const wm = document.getElementById("tsaStudentWatermark");
        if (!wm) return;

        const userId = wm.dataset.userId || "NO-ID";
        const email = wm.dataset.userEmail || wm.dataset.userName || "STUDENT";
        const now = new Date().toLocaleDateString("vi-VN");

        const mark = `ID ${userId} - ${email} - ${now}`;
        wm.setAttribute("data-watermark-text", repeatText(mark, 120));

        document.body.classList.add("tsa-student-secure");

        document.addEventListener("contextmenu", function (e) {
            e.preventDefault();
        });

        document.addEventListener("keydown", function (e) {
            const key = (e.key || "").toLowerCase();
            if (
                e.key === "F12" ||
                (e.ctrlKey && e.shiftKey && ["i", "j", "c"].includes(key)) ||
                (e.ctrlKey && ["u", "s", "p"].includes(key))
            ) {
                e.preventDefault();
                return false;
            }
        });
    });
})();
