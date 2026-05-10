
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Part2Topic

for topic in Part2Topic.objects.filter(version="gioi"):
    for voice in topic.voices.all():
        if voice.order in [1, 2, 3, 4]:
            voice.question_text = f"Person {voice.order}"
            voice.save()

print("DA_CO_DINH_PERSON_1_4_CHO_MAY_GIOI")
