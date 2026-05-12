
document.addEventListener("DOMContentLoaded", function () {
    const cards = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .part-card, .tile, article, section"));

    cards.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isPart3 = text.includes("Part 3") || href.includes("part-3");
        const isPart1 = text.includes("Part 1") || href.includes("part-1");
        const isPart2 = text.includes("Part 2") || href.includes("part-2");
        const isPart4 = text.includes("Part 4") || href.includes("part-4");

        if (isPart3) {
            el.classList.add("tsa-part3-focus");
        } else if (isPart1 || isPart2 || isPart4) {
            el.classList.add("tsa-part-not-active");
        }
    });
});
