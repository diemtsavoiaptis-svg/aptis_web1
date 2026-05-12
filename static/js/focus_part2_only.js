
document.addEventListener("DOMContentLoaded", function () {
    const lockTexts = ["Part 1", "Part 3", "Part 4"];
    const focusTexts = ["Part 2"];

    const clickable = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .part-card, .tile, article, section"));

    clickable.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isPart1 = text.includes("Part 1") || href.includes("part-1") || href.endsWith("/listening/");
        const isPart3 = text.includes("Part 3") || href.includes("part-3");
        const isPart4 = text.includes("Part 4") || href.includes("part-4");
        const isPart2 = text.includes("Part 2") || href.includes("part-2");

        if (isPart2) {
            el.classList.add("tsa-part2-focus");
            return;
        }

        if (isPart1 || isPart3 || isPart4) {
            el.classList.add("tsa-part-locked");

            if (el.tagName.toLowerCase() === "a") {
                el.setAttribute("data-old-href", el.getAttribute("href") || "");
                el.removeAttribute("href");
            }

            el.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                alert("Mục này đang khóa. Hiện tại chỉ thiết kế sâu Part 2.");
                return false;
            }, true);
        }
    });
});
