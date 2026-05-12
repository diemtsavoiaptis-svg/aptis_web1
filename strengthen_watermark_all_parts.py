from pathlib import Path
import shutil
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("code_backups") / f"before_watermark_stronger_{stamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

css_file = Path("static/css/student_watermark_security.css")

if css_file.exists():
    shutil.copy2(css_file, backup_dir / "student_watermark_security.css")

css_file.write_text(r'''
/* Student watermark security - same strong visibility for Part 1/2/3/4 */
.tsa-student-watermark {
    position: fixed !important;
    inset: 0 !important;
    z-index: 2147483647 !important;
    pointer-events: none !important;
    opacity: 1 !important;
    overflow: hidden !important;
    mix-blend-mode: multiply !important;
}

.tsa-student-watermark::before {
    content: attr(data-watermark-text) !important;
    position: absolute !important;
    inset: -25% !important;
    display: block !important;
    white-space: pre !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    line-height: 5.2 !important;
    letter-spacing: 1px !important;
    color: rgba(160, 0, 24, 0.22) !important;
    transform: rotate(-22deg) !important;
    text-transform: uppercase !important;
    word-spacing: 26px !important;
    text-shadow: 0 0 1px rgba(160, 0, 24, 0.16) !important;
}

/* Keep secure behavior */
body.tsa-student-secure {
    -webkit-user-select: none;
    user-select: none;
}

body.tsa-student-secure img,
body.tsa-student-secure video,
body.tsa-student-secure audio {
    -webkit-user-drag: none;
    user-drag: none;
}
''', encoding="utf-8")

print("DONE: watermark made stronger and consistent.")
print("Backup:", backup_dir)
