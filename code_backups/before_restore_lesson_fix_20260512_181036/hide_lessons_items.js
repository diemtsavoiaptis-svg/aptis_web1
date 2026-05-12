
document.addEventListener("DOMContentLoaded", function () {
    const badTexts = [
        "Quản lý bài học",
        "Bài học",
        "Thêm, sửa và quản lý bài học hiển thị cho học viên",
        "Chọn Bài học để thay đổi"
    ];

    const candidates = Array.from(document.querySelectorAll("a, button, .card, .dashboard-card, .admin-card, section, article, .tile, .menu-link, .side-link, .sidebar-link"));

    candidates.forEach(function (el) {
        const text = (el.innerText || el.textContent || "").trim();
        const href = (el.getAttribute("href") || "").toLowerCase();

        const isLessonHref = href.includes("lesson") || href.includes("bai-hoc") || href.includes("lessons");
        const isLessonText = badTexts.some(t => text.includes(t));

        if (isLessonHref || isLessonText) {
            let target = el;

            // Nếu là link trong card dashboard thì ẩn cả card cha
            const card = el.closest(".card, .dashboard-card, .admin-card, section, article, .tile");
            if (card && !card.innerText.includes("Duyệt học viên") && !card.innerText.includes("Cảnh báo bảo mật")) {
                target = card;
            }

            target.style.setProperty("display", "none", "important");
        }
    });
});
