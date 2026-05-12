import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import ListeningPartMaterial

DATA = {
    1: "https://drive.google.com/file/d/1cgtOo8-oI5yEf-OzIxzTsZSh9MMM5NUE/view?usp=drivesdk",
    2: "https://drive.google.com/file/d/12OAEclFCQOqLud3GqnjOGoiyfPgzYeQz/view?usp=drivesdk",
    3: "https://drive.google.com/file/d/1r67GFPxD8a2WLV2JyigHgjpn5cwK2ECq/view?usp=drivesdk",
    4: "https://drive.google.com/file/d/1zwYxkiXQTIw0uOCKKkjBz-UGnK-H6Tj0/view?usp=drivesdk",
    5: "https://drive.google.com/file/d/1z6xCcchFSJsqBoWbEA0C8xM0pLkTPiM_/view?usp=drivesdk",
    6: "https://drive.google.com/file/d/1Sb8FziuoHlXZZ-wpO9JjFFMgJ_lB1Fp8/view?usp=drivesdk",
    7: "https://drive.google.com/file/d/1u-AvnEXVoabL0tXwYBk6T-P2sbgA2YlY/view?usp=drivesdk",
    8: "https://drive.google.com/file/d/16OjY_Fmlk5t9A_Y-3ymR4DkB6emFwuJh/view?usp=drivesdk",
    9: "https://drive.google.com/file/d/1WMLESIaqnfa-fCmGFdgDSEhY4-8ZcD_n/view?usp=drivesdk",
    10: "https://drive.google.com/file/d/1To47WJHMykAEqYj3ahW9XjK7n1zu8QES/view?usp=drivesdk",
    11: "https://drive.google.com/file/d/1jtxa-DwHpw6SiWbDQlYeymXdORsK8ppv/view?usp=drivesdk",
    12: "https://drive.google.com/file/d/1W-_loFs8ZTGJl5U2hsFQm4_k93HJFxg3/view?usp=drivesdk",
    13: "https://drive.google.com/file/d/1Bs1zsSKu6q8aVMhZawNzoWWFZubUKMOF/view?usp=drivesdk",
    14: "https://drive.google.com/file/d/1VKF3bEGoCNdBjPcf-LjJlWx4Htl1egdv/view?usp=drivesdk",
    15: "https://drive.google.com/file/d/1G4YrEgXh3LkIqh2oTD3HvNgDlJAYOSSL/view?usp=drivesdk",
}

materials = list(ListeningPartMaterial.objects.filter(part=4).order_by("id"))

print("Current Part 4 materials:")
for i, m in enumerate(materials, start=1):
    print(f"{i}. ID={m.id} | {m.title} | audio={m.audio_url or 'EMPTY'}")

print()

if len(materials) < 15:
    print(f"WARNING: Database hiện chỉ có {len(materials)} material Part 4, nhưng em có 15 link audio.")
    print("Những link vượt quá số dòng database sẽ bị bỏ qua.")
    print()

updated = 0

for number, url in DATA.items():
    if number > len(materials):
        print(f"SKIP {number}: chưa có material Part 4 số {number} trong database")
        continue

    material = materials[number - 1]
    material.audio_url = url
    material.save(update_fields=["audio_url"])

    updated += 1
    print(f"OK {number}: ID={material.id} | {material.title}")

print()
print(f"Done. Updated {updated} Part 4 audio links.")
