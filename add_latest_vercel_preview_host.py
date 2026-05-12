from pathlib import Path

settings_path = Path("config/settings.py")
text = settings_path.read_text(encoding="utf-8-sig")

extra = '''
# === EXTRA VERCEL PREVIEW HOSTS START ===
EXTRA_VERCEL_PREVIEW_HOSTS = [
    "aptis-web1-4kguv4sy9-diem-tsa-voi-aptis-s-projects.vercel.app",
    "aptis-web1-ovcmk9s15-diem-tsa-voi-aptis-s-projects.vercel.app",
]

for host in EXTRA_VERCEL_PREVIEW_HOSTS:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

for host in EXTRA_VERCEL_PREVIEW_HOSTS:
    origin = f"https://{host}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
# === EXTRA VERCEL PREVIEW HOSTS END ===
'''

start = "# === EXTRA VERCEL PREVIEW HOSTS START ==="
end = "# === EXTRA VERCEL PREVIEW HOSTS END ==="

if start in text and end in text:
    before = text.split(start)[0].rstrip()
    after = text.split(end, 1)[1].lstrip()
    text = before + "\n" + extra + "\n" + after
else:
    text = text.rstrip() + "\n" + extra + "\n"

settings_path.write_text(text, encoding="utf-8")
print("Added latest Vercel preview hosts.")
