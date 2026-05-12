
document.addEventListener("DOMContentLoaded", function () {
    const rules = [
        { part: "Part 1", href: "/dashboard/part-1/", label: "Mở Part 1" },
        { part: "Part 2", href: "/dashboard/part-2/", label: "Mở Part 2" },
        { part: "Part 3", href: "/dashboard/part-3/", label: "Mở Part 3" },
        { part: "Part 4", href: "/dashboard/part-4/", label: "Mở Part 4" },
    ];

    const possibleCards = Array.from(document.querySelectorAll(".card, .dashboard-card, .part-card, .tile, article, section, div"));

    rules.forEach(function (rule) {
        const cards = possibleCards.filter(function (el) {
            const txt = (el.innerText || el.textContent || "").trim();
            return txt.includes(rule.part) && !txt.includes("Part 1\nPart 2\nPart 3\nPart 4");
        });

        cards.forEach(function (card) {
            const buttons = Array.from(card.querySelectorAll("a, button"));
            buttons.forEach(function (btn) {
                const txt = (btn.innerText || btn.textContent || "").trim();

                if (txt.includes("Mở Part") || txt.includes("Mở ")) {
                    btn.innerText = rule.label;

                    if (btn.tagName.toLowerCase() === "a") {
                        btn.setAttribute("href", rule.href);
                    } else {
                        btn.onclick = function (e) {
                            e.preventDefault();
                            window.location.href = rule.href;
                        };
                    }
                }
            });
        });
    });
});
