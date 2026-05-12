
document.addEventListener("DOMContentLoaded", function () {
    function cleanText(s) {
        return (s || "")
            .replace(/tiế\s*[\u0300-\u036f]\s*p/g, "tiếp")
            .replace(/tiê\s*[\u0300-\u036f]\s*p/g, "tiếp")
            .replace(/tiế\s+p/g, "tiếp")
            .replace(/chi\s+tiế\s*[\u0300-\u036f]\s*t/g, "chi tiết")
            .replace(/chi\s+tiê\s*[\u0300-\u036f]\s*t/g, "chi tiết")
            .replace(/chi\s+tiế\s+t/g, "chi tiết");
    }

    document.querySelectorAll("*").forEach(function (el) {
        if (el.children.length === 0 && el.textContent) {
            const fixed = cleanText(el.textContent);
            if (fixed !== el.textContent) el.textContent = fixed;
        }
    });

    const cards = Array.from(document.querySelectorAll(".card, .dashboard-card, .part-card, article, section, div"));

    cards.forEach(function (card) {
        const txt = (card.innerText || card.textContent || "");

        if (txt.includes("Part 3")) {
            card.querySelectorAll("a, button").forEach(function (btn) {
                const t = (btn.innerText || btn.textContent || "");
                if (t.includes("Mở Part")) {
                    btn.innerText = "Mở Part 3";
                    if (btn.tagName.toLowerCase() === "a") btn.href = "/dashboard/part-3/";
                    btn.onclick = function(e) {
                        if (btn.tagName.toLowerCase() !== "a") {
                            e.preventDefault();
                            window.location.href = "/dashboard/part-3/";
                        }
                    };
                }
            });
        }

        if (txt.includes("Part 4")) {
            card.querySelectorAll("a, button").forEach(function (btn) {
                const t = (btn.innerText || btn.textContent || "");
                if (t.includes("Mở Part")) {
                    btn.innerText = "Mở Part 4";
                    if (btn.tagName.toLowerCase() === "a") btn.href = "/dashboard/part-4/";
                    btn.onclick = function(e) {
                        if (btn.tagName.toLowerCase() !== "a") {
                            e.preventDefault();
                            window.location.href = "/dashboard/part-4/";
                        }
                    };
                }
            });
        }
    });
});
