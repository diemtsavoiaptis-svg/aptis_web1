from pathlib import Path

settings_path = Path("config/settings.py")
text = settings_path.read_text(encoding="utf-8-sig")

# 1) Add GZipMiddleware near top of middleware
if "'django.middleware.gzip.GZipMiddleware'," not in text:
    text = text.replace(
        "'django.middleware.security.SecurityMiddleware',",
        "'django.middleware.security.SecurityMiddleware',\n    'django.middleware.gzip.GZipMiddleware',"
    )

# 2) Ensure WhiteNoise is enabled
if "'whitenoise.middleware.WhiteNoiseMiddleware'," not in text:
    text = text.replace(
        "'django.middleware.gzip.GZipMiddleware',",
        "'django.middleware.gzip.GZipMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
    )

# 3) Add strong static compression/cache settings at bottom
patch = r'''

# === STATIC SPEED OPTIMIZATION START ===
# Compress static files and allow browser/CDN caching.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_USE_FINDERS = False

# Trust Vercel proxy HTTPS header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# === STATIC SPEED OPTIMIZATION END ===
'''

start = "# === STATIC SPEED OPTIMIZATION START ==="
end = "# === STATIC SPEED OPTIMIZATION END ==="

if start in text and end in text:
    before = text.split(start)[0].rstrip()
    after = text.split(end, 1)[1].lstrip()
    text = before + "\n" + patch + "\n" + after
else:
    text = text.rstrip() + "\n" + patch + "\n"

settings_path.write_text(text, encoding="utf-8")

# 4) Add brotli package for better compression support
req = Path("requirements.txt")
req_text = req.read_text(encoding="utf-8-sig") if req.exists() else ""

if "brotli" not in req_text.lower():
    req_text = req_text.rstrip() + "\nbrotli\n"
    req.write_text(req_text, encoding="utf-8")

print("Done: enabled GZip, WhiteNoise compression, static cache, and Brotli package.")
