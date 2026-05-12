import os
import json
from pathlib import Path
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

ONLINE_DATABASE_URL = os.environ.get("ONLINE_DATABASE_URL", "").strip()

if ONLINE_DATABASE_URL:
    import dj_database_url
    from django.conf import settings
    settings.DATABASES["online"] = dj_database_url.parse(
        ONLINE_DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )

import django
django.setup()

from django.forms.models import model_to_dict
from django.db import transaction
from core.models import ListeningPartMaterial, ListeningPartQuestion

BASE_DIR = Path(__file__).resolve().parent

DATA = {
    "1": "https://drive.google.com/file/d/1cgtOo8-oI5yEf-OzIxzTsZSh9MMM5NUE/view?usp=drivesdk",
    "2": "https://drive.google.com/file/d/12OAEclFCQOqLud3GqnjOGoiyfPgzYeQz/view?usp=drivesdk",
    "3": "https://drive.google.com/file/d/1r67GFPxD8a2WLV2JyigHgjpn5cwK2ECq/view?usp=drivesdk",
    "4": "https://drive.google.com/file/d/1zwYxkiXQTIw0uOCKKkjBz-UGnK-H6Tj0/view?usp=drivesdk",
    "5": "https://drive.google.com/file/d/1z6xCcchFSJsqBoWbEA0C8xM0pLkTPiM_/view?usp=drivesdk",
    "6": "https://drive.google.com/file/d/1Sb8FziuoHlXZZ-wpO9JjFFMgJ_lB1Fp8/view?usp=drivesdk",
    "7": "https://drive.google.com/file/d/1u-AvnEXVoabL0tXwYBk6T-P2sbgA2YlY/view?usp=drivesdk",
    "8": "https://drive.google.com/file/d/16OjY_Fmlk5t9A_Y-3ymR4DkB6emFwuJh/view?usp=drivesdk",
    "9": "https://drive.google.com/file/d/1WMLESIaqnfa-fCmGFdgDSEhY4-8ZcD_n/view?usp=drivesdk",
    "10": "https://drive.google.com/file/d/1To47WJHMykAEqYj3ahW9XjK7n1zu8QES/view?usp=drivesdk",
    "11": "https://drive.google.com/file/d/1jtxa-DwHpw6SiWbDQlYeymXdORsK8ppv/view?usp=drivesdk",
    "12": "https://drive.google.com/file/d/1W-_loFs8ZTGJl5U2hsFQm4_k93HJFxg3/view?usp=drivesdk",
    "13": "https://drive.google.com/file/d/1Bs1zsSKu6q8aVMhZawNzoWWFZubUKMOF/view?usp=drivesdk",
    "14": "https://drive.google.com/file/d/1VKF3bEGoCNdBjPcf-LjJlWx4Htl1egdv/view?usp=drivesdk",
    "15": "https://drive.google.com/file/d/1G4YrEgXh3LkIqh2oTD3HvNgDlJAYOSSL/view?usp=drivesdk",
    "16": "https://drive.google.com/file/d/13ZaotiJqGRlFfrt2QZGhs1Yhbxefzn4o/view?usp=drivesdk",
    "17": "https://drive.google.com/file/d/17UijlOVZvitTKx1E-bIdV9BG2E7UTQwz/view?usp=drivesdk",
    "18": "https://drive.google.com/file/d/1x9zeYyVD4cbAwFE2b1ZaiEtgz_OAcyQK/view?usp=drivesdk",
    "19": "https://drive.google.com/file/d/1bLnosuEItzQkEp7epleTRDTPSHGxhgFy/view?usp=drivesdk",
    "20": "https://drive.google.com/file/d/1RNK4cB8u97DfROe1VZLk2_nF6N1IqAMR/view?usp=drivesdk",
    "21": "https://drive.google.com/file/d/1kiIIg-j3kJccnsG8byxOpjEoz81uP0Xd/view?usp=drivesdk",
    "22": "https://drive.google.com/file/d/1fOHhKng39mnPRkjhSmIoBf-dJQdyKcJe/view?usp=drivesdk",
    "23": "https://drive.google.com/file/d/16j9uEc2cirbVQO18onChwwHTVohnMfJ9/view?usp=drivesdk",
    "24": "https://drive.google.com/file/d/1_E47DoBMCfd2QuKkIkPu8a_bHLXp9s1r/view?usp=drivesdk",
    "25": "https://drive.google.com/file/d/1ls94H4-7fUxkuC83tJBFB6cXf94NeZOj/view?usp=drivesdk",
    "26": "https://drive.google.com/file/d/1upq0w86daNSY_KAV0tPsB98wqOPYMzCT/view?usp=drivesdk",
    "27": "https://drive.google.com/file/d/1cjrYcvjUFMMHjt80vr0oPxAu7Ft1HG-N/view?usp=drivesdk",
    "28": "https://drive.google.com/file/d/1M6lRB5jgBj_t2zCpHOXdexI9f5XGwutG/view?usp=drivesdk",
    "29": "https://drive.google.com/file/d/1c4pmCdm5oTtBySvw3A4OU6-9xsmygSFM/view?usp=drivesdk",
    "30": "https://drive.google.com/file/d/1IkFFp6VO1Iy7j9kSzZEcBphl52QMxtzO/view?usp=drivesdk",
    "31": "https://drive.google.com/file/d/1ckMUe6tPSyf7xzzDt30IT_tOI_IRjM4u/view?usp=drivesdk",
    "32": "https://drive.google.com/file/d/160WuB4e1ZyDT3MVE3hmlpbzrURChH9Yd/view?usp=drivesdk",
    "33": "https://drive.google.com/file/d/1kUHE_SDNzL9V-nhiSmHxLjDnEvhtQQuC/view?usp=drivesdk",
    "34": "https://drive.google.com/file/d/1juMOVz6C1tWVk42HpAugEL3Kuc8bUjLG/view?usp=drivesdk",
    "35": "https://drive.google.com/file/d/1wfNmvtvA970VRBgBxIMjs0I1LF5uBDHf/view?usp=drivesdk",
    "36": "https://drive.google.com/file/d/14G2eu4TDFirXllwvZo6hR4doFvTDX_BU/view?usp=drivesdk",
    "37": "https://drive.google.com/file/d/14BuLteu581uGUTBmPK-YvCcEmuw5oBWy/view?usp=drivesdk",
    "38": "https://drive.google.com/file/d/1JZHivYN6Ehnx9kr6LqLv0karKDaGpW39/view?usp=drivesdk",
    "39": "https://drive.google.com/file/d/1Bavr7qt7NQy7OgtdkbeoanpmWzc0qCA1/view?usp=drivesdk",
    "40": "https://drive.google.com/file/d/1qtHyibBt2AkL0TSpAL8OWU_dLm49C3et/view?usp=drivesdk",
    "41": "https://drive.google.com/file/d/1iCzi74fcu1zAQLmymclVrygophpaKMX4/view?usp=drivesdk",
    "42": "https://drive.google.com/file/d/11Z0WdA8lEvC8eymJ5U-74f8b_hnghzOV/view?usp=drivesdk",
    "43": "https://drive.google.com/file/d/11p8o8k4ebrDd69mq-2WXZgiYkqrSYtmj/view?usp=drivesdk",
    "44": "https://drive.google.com/file/d/1j2plpeS1KI4UgPbL8v6lnGf1iIAG7pij/view?usp=drivesdk",
    "45": "https://drive.google.com/file/d/1jAIyecmw3p3a-Jtog6mMo_LZuu4uGKyT/view?usp=drivesdk",
    "46": "https://drive.google.com/file/d/1ic_TuyPV4pqjnmZE8yh9H1Q6kJGXv58I/view?usp=drivesdk",
    "47": "https://drive.google.com/file/d/1aDMcaYTVNDOgos8J_2OaDG-nA-gE7GX8/view?usp=drivesdk",
    "48": "https://drive.google.com/file/d/1JdBDAjQG56dn8fbL7mtwBuVun37CN02R/view?usp=drivesdk",
    "49": "https://drive.google.com/file/d/1Y2WXPFdSdFhMA6nLTz8bF372pveKFQ1A/view?usp=drivesdk",
    "50": "https://drive.google.com/file/d/1BtNXxbW0NEy7cWkg2gZ6IW0mx3TzuFVH/view?usp=drivesdk",
    "51": "https://drive.google.com/file/d/1PbD0azpnbMVgDalv082gAHTzdXME6anV/view?usp=drivesdk",
    "52": "https://drive.google.com/file/d/15gRV_gdOU5UXM-gcPn9LWRaJRwuUPj72/view?usp=drivesdk",
    "53": "https://drive.google.com/file/d/1JnYcLv39bYnW3xhYnpVw_ew-KhgyP4Qr/view?usp=drivesdk",
    "54": "https://drive.google.com/file/d/161VQLvPvkCXJhYSiZym9XU_7CMLgLcv4/view?usp=drivesdk",
}

def backup(alias):
    backup_dir = BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    path = backup_dir / f"part4_before_dedupe_{alias}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    materials = list(ListeningPartMaterial.objects.using(alias).filter(part=4).order_by("id"))
    questions = list(ListeningPartQuestion.objects.using(alias).filter(material__part=4).order_by("id"))

    data = {
        "materials": [{"id": x.id, **model_to_dict(x)} for x in materials],
        "questions": [{"id": x.id, **model_to_dict(x)} for x in questions],
    }

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Backup saved for {alias}: {path}")

def clean(alias):
    print()
    print(f"===== CLEANING {alias} =====")
    backup(alias)

    materials = list(ListeningPartMaterial.objects.using(alias).filter(part=4).order_by("id"))
    print("Before materials:", len(materials))
    print("Before questions:", ListeningPartQuestion.objects.using(alias).filter(material__part=4).count())

    by_number = {}
    for m in materials:
        key = (m.description or "").strip()
        by_number.setdefault(key, []).append(m)

    keep_ids = []

    with transaction.atomic(using=alias):
        for number in [str(i) for i in range(1, 55)]:
            candidates = by_number.get(number, [])

            if not candidates and len(materials) >= int(number):
                candidates = [materials[int(number) - 1]]

            if not candidates:
                print(f"MISSING {number}: no row found")
                continue

            def score(m):
                q_count = ListeningPartQuestion.objects.using(alias).filter(material_id=m.id).count()
                return (
                    1 if m.audio_url else 0,
                    q_count,
                    -m.id,
                )

            chosen = sorted(candidates, key=score, reverse=True)[0]

            chosen.description = number
            chosen.audio_url = DATA[number]
            chosen.save(using=alias, update_fields=["description", "audio_url"])

            keep_ids.append(chosen.id)
            print(f"KEEP {number}: ID={chosen.id} | {chosen.title}")

        delete_qs = ListeningPartMaterial.objects.using(alias).filter(part=4).exclude(id__in=keep_ids)
        deleted_count = delete_qs.count()
        delete_qs.delete()

    after_materials = ListeningPartMaterial.objects.using(alias).filter(part=4).count()
    after_questions = ListeningPartQuestion.objects.using(alias).filter(material__part=4).count()
    after_audio = ListeningPartMaterial.objects.using(alias).filter(part=4).exclude(audio_url="").count()

    print("Deleted duplicate materials:", deleted_count)
    print("After materials:", after_materials)
    print("After questions:", after_questions)
    print("After audio rows:", after_audio)

aliases = ["default"]
if ONLINE_DATABASE_URL:
    aliases.append("online")

for alias in aliases:
    clean(alias)

print()
print("DONE: Part 4 deduped to 54 rows and audio 1-54 restored.")
