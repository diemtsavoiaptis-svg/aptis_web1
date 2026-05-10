
import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core import serializers
from django.apps import apps

models_to_export = []

for model_name in ["ListeningQuestion", "Lesson"]:
    try:
        model = apps.get_model("core", model_name)
        models_to_export.extend(list(model.objects.all()))
        print(f"OK export core.{model_name}: {model.objects.count()} records")
    except LookupError:
        print(f"SKIP core.{model_name}: model không tồn tại")

Path = __import__("pathlib").Path
Path("data").mkdir(exist_ok=True)

json_text = serializers.serialize(
    "json",
    models_to_export,
    indent=2,
    ensure_ascii=False,
)

Path("data/content_seed.json").write_text(json_text, encoding="utf-8")
print("DA_EXPORT_UTF8:", len(models_to_export), "records -> data/content_seed.json")
