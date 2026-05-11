from pathlib import Path

path = Path("config/settings.py")
text = path.read_text(encoding="utf-8")

text = text.replace('    "diemtsavoiaptis.pythonanywhere.com",\n', '')
text = text.replace('    "https://diemtsavoiaptis.pythonanywhere.com",\n', '')
text = text.replace('    "http://diemtsavoiaptis.pythonanywhere.com",\n', '')

# Ensure tsaptis.com domains stay enabled
if '    "tsaptis.com",' not in text:
    text = text.replace('    ".onrender.com",\n', '    ".onrender.com",\n    "tsaptis.com",\n')
if '    "www.tsaptis.com",' not in text:
    text = text.replace('    "tsaptis.com",\n', '    "tsaptis.com",\n    "www.tsaptis.com",\n')

if '    "https://tsaptis.com",' not in text:
    text = text.replace('    "http://127.0.0.1:8000",\n', '    "http://127.0.0.1:8000",\n    "https://tsaptis.com",\n')
if '    "https://www.tsaptis.com",' not in text:
    text = text.replace('    "https://tsaptis.com",\n', '    "https://tsaptis.com",\n    "https://www.tsaptis.com",\n')

path.write_text(text, encoding="utf-8")

print("Updated config/settings.py")
print("Removed: diemtsavoiaptis.pythonanywhere.com")
print("Kept: tsaptis.com, www.tsaptis.com")
