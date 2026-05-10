from pathlib import Path

p = Path("core/views.py")
s = p.read_text(encoding="utf-8", errors="ignore")

imports = [
    "from django.contrib.auth.decorators import user_passes_test",
    "from django.views.decorators.csrf import csrf_exempt",
    "from django.contrib import messages",
    "from django.db.models import Q",
    "from django.shortcuts import render, redirect",
]

missing = [line for line in imports if line not in s]

if missing:
    s = "\n".join(missing) + "\n" + s

p.write_text(s, encoding="utf-8")
print("DA_THEM_IMPORT_THIEU_TRONG_CORE_VIEWS")
