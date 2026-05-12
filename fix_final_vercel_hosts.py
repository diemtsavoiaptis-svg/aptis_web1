from pathlib import Path

settings_path = Path("config/settings.py")
text = settings_path.read_text(encoding="utf-8-sig")

patch = r'''

# === FINAL VERCEL HOST FIX START ===
# This must stay at the bottom of settings.py.
VERCEL_URL = os.environ.get("VERCEL_URL", "").strip()

FINAL_ALLOWED_HOSTS = [
    ".vercel.app",
    "aptis-web1-ovcmk9s15-diem-tsa-voi-aptis-s-projects.vercel.app",
    "diemtsavoiaptis.io.vn",
    "www.diemtsavoiaptis.io.vn",
    "localhost",
    "127.0.0.1",
]

if VERCEL_URL:
    FINAL_ALLOWED_HOSTS.append(VERCEL_URL)

for host in FINAL_ALLOWED_HOSTS:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

FINAL_CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://aptis-web1-ovcmk9s15-diem-tsa-voi-aptis-s-projects.vercel.app",
    "https://diemtsavoiaptis.io.vn",
    "https://www.diemtsavoiaptis.io.vn",
]

if VERCEL_URL:
    FINAL_CSRF_TRUSTED_ORIGINS.append(f"https://{VERCEL_URL}")

for origin in FINAL_CSRF_TRUSTED_ORIGINS:
    if origin and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

DEBUG = False
# === FINAL VERCEL HOST FIX END ===
'''

start = "# === FINAL VERCEL HOST FIX START ==="
end = "# === FINAL VERCEL HOST FIX END ==="

if start in text and end in text:
    before = text.split(start)[0].rstrip()
    after = text.split(end, 1)[1].lstrip()
    text = before + "\n" + patch + "\n" + after
else:
    text = text.rstrip() + "\n" + patch + "\n"

settings_path.write_text(text, encoding="utf-8")
print("Fixed final Vercel ALLOWED_HOSTS and CSRF settings.")
