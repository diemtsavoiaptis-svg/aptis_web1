
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.apps import apps

try:
    SecurityAlert = apps.get_model("core", "SecurityAlert")
except LookupError:
    print("KHONG_CO_MODEL_SecurityAlert")
    raise SystemExit

qs = SecurityAlert.objects.filter(reason__icontains="rời khỏi tab")
count = qs.count()
qs.delete()

print("DA_XOA_CANH_BAO_ROI_TAB_CU:", count)
