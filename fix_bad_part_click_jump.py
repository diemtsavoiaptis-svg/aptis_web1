from pathlib import Path
import re

changed = []

# ==================================================
# 1) XÓA TOÀN BỘ JS CLICK RỘNG ĐANG GÂY NHẢY SAI
# ==================================================
for p in Path("templates").rglob("*.html"):
    s = p.read_text(encoding="utf-8", errors="ignore")
    old = s

    s = re.sub(
        r'\s*<script class="whole-part-card-click-fix">[\s\S]*?</script>\s*',
        '\n',
        s,
        flags=re.S
    )

    s = re.sub(
        r'\s*<script>\s*\(function makeWholePartCardsClickable\(\)[\s\S]*?</script>\s*',
        '\n',
        s,
        flags=re.S
    )

    if s != old:
        p.write_text(s, encoding="utf-8")
        changed.append(str(p))

print("DA_XOA_JS_CLICK_RONG_GAY_NHAY_SAI")
for f in changed:
    print("DA_SUA:", f)


# ==================================================
# 2) THÊM CLICK AN TOÀN CHỈ CHO TRANG CHỌN PART
# ==================================================
safe_js = r'''
<script>
(function safePartCardClickOnly(){
    const path = window.location.pathname;

    const isAdminPartPage =
        path === "/dashboard/listening-parts/" ||
        path === "/dashboard/listening-parts";

    const isStudentListeningPage =
        path === "/listening/" ||
        path === "/listening";

    if(!isAdminPartPage && !isStudentListeningPage) return;

    const adminLinks = {
        "1": "/dashboard/part-1/",
        "2": "/dashboard/part-2/",
        "3": "/dashboard/part-3/",
        "4": "/dashboard/part-4/"
    };

    const studentLinks = {
        "1": "/listening/",
        "2": "/listening/part-2/",
        "3": "/listening/part-3/",
        "4": "/listening/part-4/"
    };

    const links = isStudentListeningPage studentLinks : adminLinks;

    document.querySelectorAll(".part-card, .part-item, .card, article").forEach(card => {
        const text = (card.innerText || "").replace(/\s+/g, " ");
        const match = text.match(/\bPart\s*([1-4])\b/i);
        if(!match) return;

        const partNo = match[1];
        const url = links[partNo];
        if(!url) return;

        const rect = card.getBoundingClientRect();
        if(rect.width < 120 || rect.height < 80) return;

        card.style.cursor = "pointer";
        card.setAttribute("role", "button");
        card.setAttribute("tabindex", "0");

        card.addEventListener("click", function(e){
            if(e.target.closest("a, button, input, textarea, select, label")) return;
            window.location.href = url;
        });

        card.addEventListener("keydown", function(e){
            if(e.key === "Enter" || e.key === " "){
                e.preventDefault();
                window.location.href = url;
            }
        });
    });
})();
</script>
'''

# Chỉ chèn vào các template có khả năng là trang chọn Part
target_keywords = [
    "dashboard/listening-parts",
    "Choose Part",
    "Listening Practice",
    "Part 1",
    "Part 2",
    "Part 3",
    "Part 4",
]

for p in Path("templates").rglob("*.html"):
    s = p.read_text(encoding="utf-8", errors="ignore")
    old = s

    if "safePartCardClickOnly" in s:
        continue

    name = str(p).lower()
    is_likely_part_page = (
        "listening" in name and
        any(k in s for k in ["Part 1", "Part 2", "Part 3", "Part 4"])
    )

    # Không chèn vào dashboard chính/sidebar/admin chi tiết
    if is_likely_part_page and "admin_part2_gioi_detail" not in name:
        s = s.replace("</body>", safe_js + "\n</body>")
        p.write_text(s, encoding="utf-8")
        print("DA_THEM_CLICK_AN_TOAN:", p)

print("DA_FIX_XONG_CLICK_O_PART_KHONG_CON_NHAY_SAI")
