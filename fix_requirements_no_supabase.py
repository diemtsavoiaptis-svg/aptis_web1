from pathlib import Path

Path("requirements.txt").write_text("""Django>=5.2,<6.0
gunicorn
whitenoise
dj-database-url
psycopg2-binary
python-dotenv
requests
pillow
""", encoding="utf-8")

print("DA_BO_SUPABASE_PACKAGE_KHOI_REQUIREMENTS")
