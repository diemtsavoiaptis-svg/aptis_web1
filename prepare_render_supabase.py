from pathlib import Path
import re

# ==============================
# 1) Ghi requirements.txt chuẩn cho Render + Supabase PostgreSQL
# ==============================
Path("requirements.txt").write_text("""Django>=5.2,<6.0
gunicorn
whitenoise
dj-database-url
psycopg2-binary
python-dotenv
requests
supabase
pillow
""", encoding="utf-8")


# ==============================
# 2) Tạo build.sh cho Render
# ==============================
Path("build.sh").write_text("""#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
""", encoding="utf-8")


# ==============================
# 3) Tạo Procfile cho Render/Gunicorn
# ==============================
Path("Procfile").write_text("""web: gunicorn config.wsgi:application
""", encoding="utf-8")


# ==============================
# 4) Tạo file hướng dẫn biến môi trường
# ==============================
Path(".env.render.example").write_text("""# Render Environment Variables
SECRET_KEY=tao_secret_key_moi_va_dan_vao_day
DEBUG=False
DATABASE_URL=dan_supabase_database_connection_string_vao_day
CUSTOM_DOMAIN=tenmiencuaban.com

# Nếu đang dùng Supabase Storage/audio thì thêm các biến này nếu project cần
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET_NAME=your-bucket-name
""", encoding="utf-8")


# ==============================
# 5) Sửa config/settings.py để dùng DATABASE_URL
# ==============================
settings_path = Path("config/settings.py")
s = settings_path.read_text(encoding="utf-8", errors="ignore")

# Thêm import cần thiết
if "import os" not in s:
    s = "import os\n" + s

if "import dj_database_url" not in s:
    s = s.replace("import os\n", "import os\nimport dj_database_url\n", 1)

# SECRET_KEY lấy từ ENV nếu có
s = re.sub(
    r"SECRET_KEY\s*=\s*['\"][\s\S]*?['\"]",
    "SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')",
    s,
    count=1
)

# DEBUG lấy từ ENV
s = re.sub(
    r"DEBUG\s*=\s*(True|False)",
    "DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'",
    s,
    count=1
)

# ALLOWED_HOSTS mở cho Render + domain riêng
s = re.sub(
    r"ALLOWED_HOSTS\s*=\s*\[[\s\S]*?\]",
    """ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".onrender.com",
]""",
    s,
    count=1
)

# Thêm WhiteNoise middleware nếu chưa có
if "whitenoise.middleware.WhiteNoiseMiddleware" not in s:
    s = s.replace(
        "'django.middleware.security.SecurityMiddleware',",
        "'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
    )

# Override DATABASES ở cuối file để dùng DATABASE_URL nếu có, fallback SQLite local nếu không có
render_block = r'''

# ==============================
# Render + Supabase PostgreSQL config
# Local vẫn dùng db.sqlite3 nếu chưa có DATABASE_URL
# ==============================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=bool(os.environ.get("DATABASE_URL")),
    )
}

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN")

for host in [RENDER_EXTERNAL_HOSTNAME, CUSTOM_DOMAIN]:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

CSRF_TRUSTED_ORIGINS = []
for host in [RENDER_EXTERNAL_HOSTNAME, CUSTOM_DOMAIN]:
    if host:
        CSRF_TRUSTED_ORIGINS.append(f"https://{host}")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
'''

if "Render + Supabase PostgreSQL config" not in s:
    s += render_block

settings_path.write_text(s, encoding="utf-8")


# ==============================
# 6) Cập nhật .gitignore
# ==============================
gitignore = Path(".gitignore")
old = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""

need = """
venv/
__pycache__/
*.pyc
db.sqlite3
.env
.env.local
media/
staticfiles/
*.log
.DS_Store
"""

for line in need.strip().splitlines():
    if line not in old:
        old += "\n" + line

gitignore.write_text(old.strip() + "\n", encoding="utf-8")


print("DA_CHUAN_BI_XONG_RENDER_SUPABASE")
