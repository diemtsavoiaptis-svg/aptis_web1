from pathlib import Path

files = [
    Path("templates/core/listening_part2.html"),
    Path("templates/core/listening_part_placeholder.html"),
]

for p in files:
    if not p.exists():
        continue

    s = p.read_text(encoding="utf-8", errors="ignore")
    old = s

    # Add CSS nút thoát nếu chưa có
    if "back-exit-btn" not in s:
        css = """
.back-exit-btn{
    position: fixed;
    top: 18px;
    right: 22px;
    z-index: 9999;
    min-height: 46px;
    padding: 0 18px;
    border-radius: 999px;
    background: linear-gradient(135deg,#e60023,#ff5f76);
    color: white !important;
    text-decoration: none !important;
    font-weight: 900;
    font-size: 15px;
    box-shadow: 0 14px 28px rgba(230,0,35,.18);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.back-exit-btn:hover{
    filter: brightness(.96);
    transform: translateY(-1px);
}
@media(max-width:700px){
    .back-exit-btn{
        top: 12px;
        right: 12px;
        min-height: 42px;
        padding: 0 14px;
        font-size: 14px;
    }
}
"""
        if "</style>" in s:
            s = s.replace("</style>", css + "\n</style>", 1)

    # Add nút ngay sau <body>
    if "← Exit" not in s and "<body" in s:
        import re
        s = re.sub(
            r"(<body[^>]*>)",
            r'\1\n<a class="back-exit-btn" href="/dashboard/listening-parts/">← Exit</a>',
            s,
            count=1
        )

    if s != old:
        p.write_text(s, encoding="utf-8")
        print("DA_THEM_NUT_THOAT:", p)

print("DA_THEM_NUT_THOAT_QUAY_LAI_CHON_PART")
