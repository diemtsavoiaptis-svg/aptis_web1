from pathlib import Path
import re

p = Path("templates/core/listening.html")
s = p.read_text(encoding="utf-8", errors="ignore")

old = s

# Delete block section/header chứa tiêu đề hero
patterns = [
    r'<section[^>]*>[\s\S]*?Luyện đề Aptis theo từng\s*câu[\s\S]*?</section>',
    r'<header[^>]*>[\s\S]*?Luyện đề Aptis theo từng\s*câu[\s\S]*?</header>',
    r'<div[^>]*class="[^"]*(?:hero|banner|exam-title|practice-hero)[^"]*"[^>]*>[\s\S]*?Luyện đề Aptis theo từng\s*câu[\s\S]*?</div>\s*</div>',
]

for pat in patterns:
    s = re.sub(pat, "", s, count=1, flags=re.I)

p.write_text(s, encoding="utf-8")

if s != old:
    print("DA_XOA_THEME_BANNER_LUYEN_DE")
else:
    print("CHUA_TIM_THAY_BANNER_CAN_XOA - gửi mình file listening.html nếu vẫn còn")

