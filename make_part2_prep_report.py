from pathlib import Path

files = [
    "core/models.py",
    "core/views.py",
    "core/urls.py",
    "templates/core/dashboard.html",
    "templates/core/admin_student_lookup.html",
    "templates/core/listening.html",
    "static/core/security_protect.js",
]

report = []
report.append("===== PART 2 PREP REPORT =====\n")

for f in files:
    p = Path(f)
    report.append(f"\n\n===== FILE: {f} =====\n")
    if p.exists():
        text = p.read_text(encoding="utf-8", errors="ignore")
        # In các dòng có liên quan Part/listening/dashboard
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            low = line.lower()
            if any(k in low for k in [
                "part", "listening", "admin_part", "dashboard", 
                "listeningquestion", "question", "audio", "transcript"
            ]):
                report.append(f"{i}: {line}")
    else:
        report.append("KHONG TON TAI")

Path("PART2_PREP_REPORT.txt").write_text("\n".join(report), encoding="utf-8")

print("DA_TAO_PART2_PREP_REPORT.txt")
print("Hay mo file PART2_PREP_REPORT.txt hoac copy noi dung gui lai cho minh.")
