from pathlib import Path
import re

p = Path("templates/core/listening.html")
text = p.read_text(encoding="utf-8", errors="ignore")

# backup
Path("templates/core/listening.html.bak_random_watermark").write_text(text, encoding="utf-8")

# xóa watermark cũ nếu đã từng chèn
remove_patterns = [
    r'<style[^>]*id=["\']random-watermark-style["\'][\s\S]*?</style>',
    r'<script[^>]*id=["\']random-watermark-script["\'][\s\S]*?</script>',
    r'<div[^>]*id=["\']random-watermark-layer["\'][\s\S]*?</div>',
]
for pat in remove_patterns:
    text = re.sub(pat, '', text, flags=re.IGNORECASE)

style_block = """
<style id="random-watermark-style">
  #random-watermark-layer{
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 6;
    overflow: hidden;
  }

  .random-watermark-item{
    position: absolute;
    white-space: nowrap;
    font-weight: 700;
    font-size: clamp(18px, 1.4vw, 26px);
    color: rgba(120, 0, 25, 0.12);
    transform-origin: center;
    user-select: none;
    letter-spacing: 0.6px;
    text-shadow: 0 1px 0 rgba(255,255,255,0.2);
  }
</style>
"""

script_block = """
<script id="random-watermark-script">
(function () {
  function buildWatermark() {
    const old = document.getElementById('random-watermark-layer');
    if (old) old.remove();

    const layer = document.createElement('div');
    layer.id = 'random-watermark-layer';

    const text = `{{ request.user.username|default:"APTIS" }} · {{ request.user.email|default:"admin@gmail.com" }}`;

    const w = window.innerWidth;
    const h = window.innerHeight;

    const cols = Math.max(2, Math.floor(w / 420));
    const rows = Math.max(2, Math.floor(h / 260));
    const total = Math.max(6, Math.min(12, cols * rows));

    const used = [];

    function tooClose(x, y) {
      return used.some(([ux, uy]) => Math.abs(ux - x) < 220 && Math.abs(uy - y) < 120);
    }

    for (let i = 0; i < total; i++) {
      let x = 0, y = 0, safe = 0;
      do {
        x = Math.random() * Math.max(200, w - 260);
        y = Math.random() * Math.max(120, h - 100);
        safe++;
      } while (tooClose(x, y) && safe < 40);

      used.push([x, y]);

      const item = document.createElement('div');
      item.className = 'random-watermark-item';
      item.textContent = text;

      const angle = -28 + Math.random() * 12;   // chéo nhưng không đều
      const opacity = 0.08 + Math.random() * 0.06;
      const scale = 0.90 + Math.random() * 0.18;

      item.style.left = x + 'px';
      item.style.top = y + 'px';
      item.style.opacity = opacity.toFixed(2);
      item.style.transform = `rotate(${angle}deg) scale(${scale})`;

      layer.appendChild(item);
    }

    document.body.appendChild(layer);
  }

  let timer = null;
  function rebuildLater() {
    clearTimeout(timer);
    timer = setTimeout(buildWatermark, 180);
  }

  document.addEventListener('DOMContentLoaded', buildWatermark);
  window.addEventListener('resize', rebuildLater);
})();
</script>
"""

if "</head>" in text and "random-watermark-style" not in text:
    text = text.replace("</head>", style_block + "\n</head>", 1)
else:
    text = style_block + "\n" + text

if "</body>" in text and "random-watermark-script" not in text:
    text = text.replace("</body>", script_block + "\n</body>", 1)
else:
    text += "\n" + script_block

p.write_text(text, encoding="utf-8")
print("DA_SUA_WATERMARK_CHEO_NGAU_NHIEN_VUA_PHAI")
