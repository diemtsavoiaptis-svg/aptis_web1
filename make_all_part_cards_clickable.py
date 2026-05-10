from pathlib import Path
import re

changed_files = []

# Các link Part chuẩn
part_links = {
    "1": "/dashboard/part-1/",
    "2": "/dashboard/part-2/",
    "3": "/dashboard/part-3/",
    "4": "/dashboard/part-4/",
}

student_part_links = {
    "1": "/listening/",
    "2": "/listening/part-2/",
    "3": "/listening/part-3/",
    "4": "/listening/part-4/",
}

for p in Path("templates").rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    old = text

    # ==================================================
    # 1) Với các card có data-part="1/2/3/4": thêm onclick toàn card
    # ==================================================
    for n, url in part_links.items():
        text = re.sub(
            rf'(<[^>]+class="[^"]*(?:part|card)[^"]*"[^>]*data-part="{n}"(?![^>]*onclick)[^>]*)(>)',
            rf'\1 onclick="window.location.href=\'{url}\'" role="button" tabindex="0"\2',
            text,
            flags=re.I
        )

    # ==================================================
    # 2) Với card có chữ Part 1-4 nhưng chỉ nút bên trong bấm được:
    #    thêm JS tự bắt click cả khung.
    # ==================================================
    if ("Part 1" in text or "Part 2" in text or "Part 3" in text or "Part 4" in text) and "makeWholePartCardsClickable" not in text:
        script = r'''
<script>
(function makeWholePartCardsClickable(){
    const adminLinks = {
        "Part 1": "/dashboard/part-1/",
        "Part 2": "/dashboard/part-2/",
        "Part 3": "/dashboard/part-3/",
        "Part 4": "/dashboard/part-4/"
    };

    const studentLinks = {
        "Part 1": "/listening/",
        "Part 2": "/listening/part-2/",
        "Part 3": "/listening/part-3/",
        "Part 4": "/listening/part-4/"
    };

    const isStudentPage = location.pathname.startsWith("/listening");
    const links = isStudentPage ? studentLinks : adminLinks;

    const candidates = Array.from(document.querySelectorAll("a, .card, .part-card, .part-item, article, section, div"));

    candidates.forEach(el => {
        const txt = (el.innerText || "").trim();
        if (!txt) return;

        const partName = Object.keys(links).find(name => {
            const regex = new RegExp("\\b" + name.replace(" ", "\\s*") + "\\b", "i");
            return regex.test(txt);
        });

        if (!partName) return;

        const rect = el.getBoundingClientRect();
        if (rect.width < 120 || rect.height < 80) return;

        const hasChildPartCard = Array.from(el.children || []).some(child => {
            const childText = (child.innerText || "").trim();
            return Object.keys(links).some(name => childText.includes(name)) && child.getBoundingClientRect().height > 60;
        });

        if (hasChildPartCard) return;

        el.style.cursor = "pointer";
        el.setAttribute("role", "button");
        el.setAttribute("tabindex", "0");

        el.addEventListener("click", function(e){
            if (e.target.closest("a, button, input, textarea, select, label")) return;
            window.location.href = links[partName];
        });

        el.addEventListener("keydown", function(e){
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                window.location.href = links[partName];
            }
        });
    });
})();
</script>
'''
        text = text.replace("</body>", script + "\n</body>")

    # ==================================================
    # 3) CSS hover cho card dễ nhận biết
    # ==================================================
    if ("Part 1" in text or "Part 2" in text or "Part 3" in text or "Part 4" in text) and ".part-card-clickable-hover-fix" not in text:
        css = r'''
<style class="part-card-clickable-hover-fix">
.card:hover,
.part-card:hover,
.part-item:hover,
article:hover {
    cursor: pointer;
}
</style>
'''
        text = text.replace("</head>", css + "\n</head>")

    if text != old:
        p.write_text(text, encoding="utf-8")
        changed_files.append(str(p))

print("DA_SUA_CLICK_TOAN_BO_THE_PART")
for f in changed_files:
    print("DA_SUA:", f)
