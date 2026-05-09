(function () {
    "use strict";

    document.documentElement.classList.add("tsa-protected");

    function blockEvent(event) {
        event.preventDefault();
        event.stopPropagation();
        return false;
    }

    /*
      Cho ph?p:
      - B?i ?en
      - Copy
      - Chu?t ph?i
      - Ctrl+C
      - Ctrl+A

      Ch?n:
      - Ctrl+S l?u trang
      - Ctrl+P in trang
      - Ctrl+U view source
      - F12
      - Ctrl+Shift+I/J/C
      - DevTools c? b?n b?ng ph?t hi?n k?ch th??c
      - N?t t?i audio m?c ??nh
    */

    document.addEventListener("keydown", function (event) {
        const key = String(event.key || "").toLowerCase();

        if (event.key === "F12") {
            return blockEvent(event);
        }

        if (event.ctrlKey || event.metaKey) {
            if (["s", "p", "u"].includes(key)) {
                return blockEvent(event);
            }
        }

        if (event.ctrlKey && event.shiftKey) {
            if (["i", "j", "c"].includes(key)) {
                return blockEvent(event);
            }
        }

        if (event.key === "PrintScreen") {
            try {
                navigator.clipboard.writeText("N?i dung ???c b?o v? b?i TSA Aptis.");
            } catch (error) {}
            return blockEvent(event);
        }
    }, true);

    window.addEventListener("beforeprint", function (event) {
        return blockEvent(event);
    });

    const focusShield = document.createElement("div");
    focusShield.className = "security-focus-shield";
    focusShield.innerHTML = `
        <div class="security-focus-shield-box">
            <h2>N?i dung ?ang ???c b?o v?</h2>
            <p>Vui l?ng quay l?i c?a s? h?c t?p ?? ti?p t?c l?m b?i. N?i dung ?? ???c g?n watermark theo t?i kho?n ??ng nh?p.</p>
        </div>
    `;
    document.body.appendChild(focusShield);

    const devtoolsShield = document.createElement("div");
    devtoolsShield.className = "security-devtools-shield";
    devtoolsShield.innerHTML = `
        <div class="security-devtools-box">
            <h2>Ph?t hi?n c?ng c? ki?m tra trang</h2>
            <p>Vui l?ng ??ng DevTools ?? ti?p t?c h?c. Ho?t ??ng n?y c? th? ???c ghi nh?n l? d?u hi?u b?t th??ng.</p>
        </div>
    `;
    document.body.appendChild(devtoolsShield);

    function showFocusShield() {
        focusShield.classList.add("show");
    }

    function hideFocusShield() {
        focusShield.classList.remove("show");
    }

    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            showFocusShield();
        } else {
            hideFocusShield();
        }
    });

    window.addEventListener("blur", showFocusShield);
    window.addEventListener("focus", hideFocusShield);

    function detectDevTools() {
        const threshold = 170;
        const widthGap = window.outerWidth - window.innerWidth;
        const heightGap = window.outerHeight - window.innerHeight;

        if (widthGap > threshold || heightGap > threshold) {
            devtoolsShield.classList.add("show");
        } else {
            devtoolsShield.classList.remove("show");
        }
    }

    setInterval(detectDevTools, 1000);

    setInterval(function () {
        const now = new Date();
        document.querySelectorAll("[data-security-time]").forEach(function (item) {
            item.textContent = now.toLocaleString("vi-VN");
        });
    }, 1000);

    async function loadSecureAudio(audio) {
        const url = audio.dataset.audioUrl;
        if (!url || audio.dataset.loaded === "1") {
            return;
        }

        audio.dataset.loaded = "1";

        try {
            const response = await fetch(url, {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (!response.ok) {
                throw new Error("Audio load failed");
            }

            const blob = await response.blob();
            const objectUrl = URL.createObjectURL(blob);
            audio.src = objectUrl;
        } catch (error) {
            console.warn("Kh?ng th? t?i audio b?o v?.", error);
        }
    }

    document.querySelectorAll("audio.secure-audio").forEach(function (audio) {
        audio.addEventListener("play", function () {
            loadSecureAudio(audio);
        }, { once: true });

        audio.addEventListener("mouseenter", function () {
            loadSecureAudio(audio);
        }, { once: true });
    });
})();
